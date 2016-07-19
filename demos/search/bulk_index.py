#!/usr/bin/env python

import boto3
import botocore

import xml.etree
import pprint
from datetime import datetime
import time
import os
import sys
import ConfigParser
import argparse
import re
from threading import Thread
import Queue
import logging

import json
from elasticsearch import Elasticsearch






#TODO: 
# * check ES listing against objList
# * add timings for each step/stage and report @ end
# * figure out right way to block on each queue 

class keyWorker(Thread):
	def __init__(self, queue,endpoint,key,secret,bucket,es_cluster,es_index,es_type):
		Thread.__init__(self)
		self.queue = queue

	def run(self):

		proc_name = self.name

		#Call the Connect function to setup the s3 connection, each thread makes its own connection
		s3Client = make_iggy_session(endpoint, key,secret)
	

		while True:
			count_hash['pre_kworker'] +=1

			# Get the work from the queue
			objKey = self.queue.get()
			if objKey is None:
				print("keyworker : Exiting: {}".format(proc_name))
				count_hash['post_kworker'] +=1

				obj_queue.put((None,None))
				#self.queue.task_done()
				break
			else:
				objMeta = head_object(objKey,s3Client,bucket)
				obj_queue.put((objKey,objMeta))
				count_hash['post_kworker'] +=1
				#self.queue.task_done()


class indexWorker(Thread):
	def __init__(self, queue,bucket,es_cluster,es_index,es_type):
		Thread.__init__(self)
		self.queue = queue

	def run(self):

	    proc_name = self.name

	    while True:
	    	count_hash['pre_iworker'] +=1
	        # Get the work from the queue
	        objKey,objMeta = self.queue.get()
	        if objKey is None:
	            print("objworker : Exiting: {}".format(proc_name))
	            count_hash['post_iworker'] +=1

	            #self.queue.task_done()
	            break
	        else:
				index_result = objIndexer(objKey,objMeta,bucket,es_cluster,es_index,es_type)
				count_hash['post_iworker'] +=1
				self.queue.task_done()

					#print index_result
					#self.queue.task_done()


class Ddict(dict):
    def __init__(self, default=None):
        self.default = default

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)
  


def head_object(objKey,s3client,bucket):
	count_hash['pre_head'] +=1
	method = 'head_object'
	try:
		response = s3client.head_object(
			Bucket=bucket,
			Key=objKey)
		count_hash['post_head'] +=1




	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		response = "error"
		print "erra"
		#print error_code

	return response





def objIndexer(objKey,objMeta,bucket,es_cluster,es_index,es_type):

	count_hash['pre_index'] += 1


	es = Elasticsearch(
	[es_cluster],
	port=9200
	)

	body_hash = {}
	#makes sense for ID to be the objectKey
	#index_id = phat_hash['path']

	index_id = bucket + "/" + objKey
	#print objKey

	#is this a file or dir?:
	if index_id.split('/')[-1].strip():
		#means its a file
	#
	#figure out extension, path, shortname
	#
		body_hash['extension'] = os.path.splitext(objKey)[1]
		body_hash['path'] = index_id
		body_hash['shortName'] = body_hash['path'].split('/')[-1]
		body_hash['objType'] = "file"

	else:
		#means its a dir

        #this is the child, we should put this right away
        #
		body_hash['shortName'] = body_hash['path'].split('/')[-2]
		body_hash['objType'] = "directory"


	for myKey in objMeta.keys():
		if "ResponseMetadata" in myKey:
			pass
		elif "ContentLength" in myKey:
			body_hash['content-length'] = objMeta['ContentLength']
		elif myKey == "Metadata":
			for metaKey in objMeta['Metadata'].keys():
				if 'meta-ign' in metaKey:
					metaRe = re.search('meta-ign-(.+)', metaKey)
					if  metaRe:
					#if the group contains a '-' , just grab the word
						if '-' in metaRe.group(1):
							attr = metaRe.group(1).split('-')[1]
							if 'time' in attr:
								#this is an epoch timestamp..make it an int 
								body_hash[attr] = int(float(objMeta['Metadata'][metaKey]))
							else:
								#this is either mode, uid, or gid for now, just leave as str
								body_hash[attr] = objMeta['Metadata'][metaKey]

						else:
						#this means there wasn't a '-' , so we can just use the word
							body_hash[metaRe.group(1)] = objMeta['Metadata'][metaKey]
					else:
						#this means it had meta-ign, but didn't match known pattern
						# in which case, just shove it in
						body_hash[metaKey] = objMeta['Metadata'][metaKey]
				else:
				#this is where non matched netadata keys go
					body_hash[metaKey] = objMeta['Metadata'][metaKey]

			#non-matched keys outside 'metadata'
		else:
			body_hash[myKey] = objMeta[myKey]

	body_hash['bucket'] = bucket

	res = es.index(index=es_index, doc_type=es_type, id=index_id, body=body_hash)
	count_hash['post_index'] += 1

	return res

      

def make_iggy_session(endpoint,iggy_key,iggy_secret):

	iggySession = boto3.session.Session()

	iggyClient = iggySession.client('s3',
			aws_access_key_id = iggy_key,
	        aws_secret_access_key = iggy_secret,
			endpoint_url=endpoint,
			use_ssl=False,
			verify=False,
			config=boto3.session.Config(
				signature_version='s3',
				connect_timeout=60,
				read_timeout=60,
				s3={'addressing_style': 'path'})
			)

	return iggyClient



def check_buckets(iggyClient,bucket):

	try:
		iggyBucket = iggyClient.head_bucket(Bucket=bucket)
	
	except botocore.exceptions.ClientError as e:
		#print dir(e)
		print "had an issue with bucket : %s , %s" %(bucket,e.response)
		sys.exit(1)
		#error_code = int(e.response['Error']['Code'])


	return iggyBucket
	



def list_objects(s3Client,src_bucket):		 
	#
	#note that you can only get back up to 1000 keys at a time
	# so using pagination to try and get them all.
	#
	method = 'list_objects'
	try:
		paginator = s3Client.get_paginator('list_objects')

		pages = paginator.paginate(
			Bucket=src_bucket		
			)


		return pages
	except botocore.exceptions.ClientError as e:
		print "failed"



def getArgs():

	parser = argparse.ArgumentParser(description = "index a bucket")


	parser.add_argument("-n", "--num-threads", type=int, dest="num_threads", default=5)



	parser.add_argument('--bucket', dest="bucket",
	help = "bucket to index")


	parser.add_argument('-k', '--key', dest="key",
	help = "Igneous access key")


	parser.add_argument('-s','--secret', dest="secret",
	help = "Igneous secret key")

	parser.add_argument('-e', '--endpoint',
	help = "Igneous endpoint, eg: http://igneous.company.com:80")

	parser.add_argument('-c', '--cluster',
	help = "elastic search cluster, eg: my.hostname.com",
	dest='es_cluster',
	required=True)


	parser.add_argument("-i", "--index", dest="es_index", default="demo")
	parser.add_argument("-t", "--type", dest="es_type", default="fsindex")


	args =  parser.parse_args()



	return args.endpoint,args.bucket,args.key,args.secret,args.es_cluster,args.es_index,args.es_type,args.num_threads


#########
#end of functions
#########


if __name__ == "__main__":
		#delete these 
	count_hash = Ddict( dict )
	count_hash['keyCount'] = 0
	count_hash['pre_index'] = 0
	count_hash['post_index'] = 0
	count_hash['pre_head'] = 0
	count_hash['post_head'] = 0
	count_hash['pre_iworker'] = 0
	count_hash['post_iworker'] = 0
	count_hash['pre_kworker'] = 0
	count_hash['post_kworker'] = 0




	endpoint,bucket,key,secret,es_cluster,es_index,es_type,num_threads = getArgs()




	iggyClient = make_iggy_session(endpoint,key,secret)


	iggyBucket = check_buckets(iggyClient,bucket)

	#
	#Queue flow: list keys -> key_queue , enumerate meta -> obj_queue ; perform puts into index
	#
	#a q for keys
	key_queue = Queue.Queue()

	#a queue for objects, with all the metadata we can pull per key
	obj_queue = Queue.Queue()

	for x in range(num_threads):
		kWorker = keyWorker(key_queue,endpoint,key,secret,bucket,es_cluster,es_index,es_type)
		#Setting the daemon to True will let the main thread exit even though the worker is not done
		kWorker.daemon = True
		kWorker.start()
		#and the q for full obj metadata
		iWorker = indexWorker(obj_queue,bucket,es_cluster,es_index,es_type)
		iWorker.daemon = True
		iWorker.start()



#
#first, get the list of pages
#
	objPages = list_objects(iggyClient,bucket)

#
# next, we need to check in the index to make sure the key
# doesn't already exist.  Perhaps it would make more sense to do this
# more 'smartly', but if the ES cluster is close in latency terms to
# where this script is run, then it should be relatively cheap to 
# slam through the list quickly.
#

	print "done listing"
	
	for page in objPages:
		for key in page['Contents']:
			objKey =  key['Key']
			#print objKey
			key_queue.put(objKey)
			count_hash['keyCount'] += 1






	for i in range(num_threads):
		key_queue.put(None)

	print("Waiting for threads to stop")
	
	
	kWorker.join()
	iWorker.join()

	#print "keys found : %s pre: %s post : %s" %(keyCount,pre_index,post_index)

	print(json.dumps(count_hash, indent=2))




