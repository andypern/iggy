#!/usr/bin/python3

import boto3 
import botocore 
import pathlib 
import os
import time
import sys
from multiprocessing import Process, JoinableQueue, Value


class movedatafromAWS(Process):

	def __init__(self, file_queue, queue_state, max_keys, num_threads):
		Process.__init__(self)
		self.file_queue = file_queue
		self.queue_state = queue_state
		self.max_keys = max_keys
		self.num_threads = num_threads
		self.cyclesperthread = int(max_keys/num_threads)

	def run(self):
		resource = boto3.resource('s3',
				aws_access_key_id='S3ACCESSKEY',
				aws_secret_access_key='S3SECRETACCESSKEY'
				)

		igresource = boto3.resource('s3',
				use_ssl=False,
				endpoint_url='http://demo.iggy.bz',
                		aws_access_key_id='IGNEOUSACCESSKEY',
				aws_secret_access_key='IGNEOUSSECRETACCESSKEY'
				)	
		loop_count = 1 	
		key_count = 1	
		while True:
			print("{} cycleperthread {}, key_count {}, queue_state {}, loop_count {}".format(self.name, self.cyclesperthread, key_count, self.queue_state.value, loop_count))
			if self.cyclesperthread == key_count: 
				if self.queue_state.value <= loop_count: 
					loop_count += 1
					self.queue_state.value = loop_count
				else: 
					loop_count = self.queue_state.value
				key_count = 1 
			else: 
				key_count += 1

			next_task = self.file_queue.get()

			print("{} : File {}".format(self.name, next_task))

			if next_task is None: 
				self.file_queue.task_done()
				break

			move_data(self.name, next_task, resource, igresource)

			self.file_queue.task_done()


		return

def move_data(process_name, next_task, resource, igresource): 

		max_retries = 10
		loop_again = True	

		while loop_again is True and max_retries > 0:
			try:		
				response = resource.Object('cs-multimedia',next_task).get()
				loop_again = False

			except botocore.exceptions.ClientError as e:
				print("{} S3 Failed on GET {}".format(process_name, e.response['ResponseMetadata']['HTTPStatusCode']))
				print("{} S3 Failed on KEYNAME {}".format(process_name, next_task))

				if e.response['ResponseMetadata']['HTTPStatusCode'] == 404: 
					return
				else: 
					sys.exit(1)

			except (botocore.vendored.requests.exceptions.ConnectionError, 
				botocore.vendored.requests.exceptions.ReadTimeout,
				botocore.exceptions.EndpointConnectionError) as e:
	
				print("{} S3 Timeout Error {} {} Retry {}".format(process_name, next_task, e, max_retries))
				backoff = 300 - ((2 * max_retries) * 10)
				time.sleep(backoff)
				max_retries -= 1
				if (max_retries < 0): 
					print("Could not retrieve from connection")
					sys.exit(1)


		max_retries = 10 
		loop_again = True 

		while loop_again is True and max_retries > 0:

			try: 	

				igresource.Bucket('multimedia-commons').put_object(Key=next_task, Body=response['Body'].read())	
				loop_again = False 

			except botocore.exceptions.ClientError as e:
				print("{} IG Failed on GET {}".format(process_name,e.response['ResponseMetadata']['HTTPStatusCode']))
				sys.exit(1)

			except (botocore.vendored.requests.exceptions.ConnectionError, 
				botocore.vendored.requests.exceptions.ReadTimeout,
				botocore.exceptions.EndpointConnectionError) as e:
	
				print("{} IG Timeout Error {} {} Retry {}".format(process_name,next_task, e, max_retries))
				backoff = 300 - ((2 * max_retries) * 10)
				print("{} IG Backoff {}".format(process_name, backoff))
				time.sleep(backoff)
				print("{} IG Past Sleep ".format(process_name))
				max_retries -= 1
				if (max_retries < 0): 
					print("Could not retrieve from connection")
					sys.exit(1)
		
		#resource.Object('cs-multimedia', key.key).download_file(filename)

		max_retries = 10 
		loop_again = True 

		while loop_again is True and max_retries > 0:

			try: 	
				resource.Object('cs-multimedia',next_task).delete()
				loop_again = False 

			except botocore.exceptions.ClientError as e:
				print("{} Failed on delete {}".format(process_name, e.response['ResponseMetadata']['HTTPStatusCode']))
				sys.exit(1)

			except (botocore.vendored.requests.exceptions.ConnectionError, 
				botocore.vendored.requests.exceptions.ReadTimeout,
				botocore.exceptions.EndpointConnectionError) as e:
	
				print("{} Timeout Error {} {} Retry {}".format(process_name, next_task, e, max_retries))
				backoff = 300 - ((2 * max_retries) * 10)
				time.sleep(backoff)
				max_retries -= 1
				if (max_retries < 0): 
					print("Could not retrieve from connection")
					sys.exit(1)




def connect_to_aws(file_queue, queue_state, max_keys, num_threads):

	resource = boto3.resource('s3',
				aws_access_key_id='S3ACCESSKEY',
				aws_secret_access_key='S3SECRETACCESSKEY'
				)

	my_bucket = resource.Bucket('cs-multimedia')

	key_count = 1 
	loop_count = 1

	for key in my_bucket.objects.all():
		print(key.key)
		file_queue.put(key.key)

		remainder = key_count % max_keys
		
		if remainder == 0: 
			print("connect to aws queue_state {}, loop_count {}".format(queue_state.value, loop_count))
			while queue_state.value == loop_count: 
				time.sleep(2)
			loop_count += 1

		key_count += 1

		


if __name__ == '__main__':

	file_queue = JoinableQueue()
	queue_state = 0
	max_keys = 400

	num_threads = 4 
	queue_state = Value('i', 1)

	file_processes = [ movedatafromAWS(file_queue, queue_state, max_keys, num_threads) for i in range(num_threads) ]

	for w in file_processes:
		w.start()

	connect_to_aws(file_queue, queue_state, max_keys, num_threads)

	for i in range(num_threads):
		file_queue.put(None)

	for w in file_processes: 
		w.join()
	



