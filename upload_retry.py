#!/usr/bin/env python

import boto3
import botocore
from boto3.s3.transfer import S3Transfer, TransferConfig

import logging
import xml.etree
import pprint
from datetime import datetime
import time
import os
import sys
import getopt
import re
from string import ascii_uppercase
from random import choice



logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)




########
#This is a script to put a bunch of dummy files into a a bucket.
#Use case is primarily to run tests during a planned outage such as a Petra & Lithos upgrade.
#Boto3 has some logic around retries and timeouts, but we also have to handle 500 errors
#which get returned by the server when S3liteD is UP, but some lithos are down.
#

#####
# Script connects to an S3 endpoint and attempts to upload files into a container.  You specify:
# * endpoint connection info (igneous.company.com:80)
# * target container/bucket
# * how many files to upload
# * path/name of the input file , note that it will re-use this file and upload -c <count> times
# 
# * it will clean up files it has created at the end
# * optionally you can run it with the '--delete' option to *ONLY* delete (things which may be leftover from previous runs)
#

###############
# some variables , will make this dynamic in the future.
#
urlprefix = 'http://'

#file prefix, makes it easier to filter for objects to delete

fileprefix = "file-"


#
#set defaults, some can be overriden via args
#

print_verbose = False
largeFiles = False
delete_only = False
filecount = 1000
session_timeout = 60
max_retries = 5

#
#
#
#
# end of variables
##################



#
#provide some CLI options.  
#

try:
        opts, args = getopt.getopt(sys.argv[1:], "e:a:s:b:i:c:dlr:v", 
        	["endpoint=","access_key=","secret_key=","bucket=","count=",
        	"delete","large","retries=","verbose"])
except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print "wrong option"
        sys.exit(2)


for opt, arg in opts:

	if opt in ('-e', '--endpoint'):
		endpoint = arg
	if opt in ('-a', '--access_key'):
		access_key = arg
	if opt in ('-s','--secret_key'):
		secret_key = arg
	if opt in ('-b','--bucket'):
		bucket = arg
	if opt in ('-i','--input_file'):
		input_file = arg
	if opt in ('-c','--count'):
		filecount = int(arg)
	if opt in ('-d','--delete'):
		delete_only = True
	if opt in ('-l','--large'):
		largeFiles = True
	if opt in ('-r','--retries'):
		max_retries = int(arg)
	if opt in ('-v', '--verbose'):
		print_verbose = True





#
#we require 5 arg's, plus there are some optional ones.
#

if len(opts) < 5:
	print "syntax is `./upload_retry.py -e <endpoint.company.com:80> -a <access_key> -s <secret_key> -b bucket -i input_file [-c filecount] [--delete] [--large] [-r retries] [--verbose]`"
	sys.exit(1)





######Functions#####
#
#
#


def main():
		
	s3client = make_session()

	#
	# delete_only = don't do any uploads, just cleanup.
	#
	if delete_only == True:
		print "deleting all files starting with %s/%s" %(bucket,fileprefix)
		objList =  list_objects(s3client,bucket, fileprefix)
		count = 0
		for page in objList:
			for key in page['Contents']:
				delete_object(s3client,bucket,key['Key'])
				count += 1
		print "deleted %s" %(count)
	else:

		#
		#most of the time we'll do this
		#
		print "putting %s files to %s"  %(filecount, bucket)
		upload_file(s3client,bucket, filecount, fileprefix)


		print "finished putting %s files" %(filecount)

		#
		#get a list of objects in pages, then blow them away
		#

		objList =  list_objects(s3client,bucket, fileprefix)

		count = 0
		for page in objList:
				for key in page['Contents']:
					delete_object(s3client,bucket,key['Key'])
					count += 1


		print "deleted %s" %(count)




def printfail(method,response):
	#
	#this is mainly so we have a consistent way to print 
 	#
 	#
 	if print_verbose == True:
 		print "%s,%s" % (method,response)
 	else:
		print "%s,%s" % (method,response['ResponseMetadata']['HTTPStatusCode'])


def printsuccess(method,response):
	#
	#this is mainly so we have a consistent way to print
 	#
 	#
 	if print_verbose == True:
 		print "%s,%s" % (method,response)
 	else:
 		try:	
	 		print "%s,%s" % (method,response['ResponseMetadata']['HTTPStatusCode'])
 		except TypeError as e:
 			print "%s : 200 , but had TypeError : %s" %(method,e)



	#
	#build the client session.  
	#

def make_session():


	session = boto3.session.Session()

	s3client = session.client('s3',
			aws_access_key_id = access_key,
	        aws_secret_access_key = secret_key,
			endpoint_url=urlprefix + endpoint,
			use_ssl=False,
			verify=False,
			config=boto3.session.Config(
				signature_version='s3',
				connect_timeout=session_timeout,
				read_timeout=session_timeout,
				s3={'addressing_style': 'path'})
			)



	return s3client






def list_objects(s3client,bucket, fileprefix):		 
	#
	#note that you can only get back up to 1000 keys at a time
	# so use pagination to  get them all.
	#
	method = 'list_objects'
	try:
		paginator = s3client.get_paginator('list_objects')

		pages = paginator.paginate(
			Bucket=bucket,
			Delimiter='/',
			Prefix=fileprefix
		)


		#printsuccess(method,paginator)
		return pages
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)







#
#upload & retry
#

def upload_file(s3client,bucket, filecount, fileprefix):

	# Setup the parameters for the upload 
	config = TransferConfig(
		# Set multipart_threshold to 8GB before using Multipart, effectively disabling it
    		multipart_threshold= 20 * 1024 * 1024 * 1024,  
    		max_concurrency=10,
	)


	transfer = S3Transfer(s3client, config)


	method = 'upload_file'
	#start a timer so we know how long this is all taking
	global_start_time = time.time()

	#loop through until we've uploaded <filecount> files
	for i in range(filecount):
		#measure how long each file takes
		local_start_time = time.time()
		nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
		#make a random name for each object.
		objKey = fileprefix + '-' + str(i) + '-' + (''.join(choice(ascii_uppercase) for i in range(6))) + '.file'

		try:
			response = transfer.upload_file(
				input_file, 
				bucket,
				objKey
				)
			local_elapsed_time = time.time() - local_start_time
			print "at %s made file # %s in %s" %(nowtime, i, local_elapsed_time)
			#
			#first exception will trap things like auth, no such bucket, etc
			#
		except botocore.exceptions.ClientError as e:
			printfail(method,e.response)

			#
			#these 3 exceptions trap various timeout errors.
			#
		except (botocore.vendored.requests.exceptions.ConnectionError, 
			botocore.vendored.requests.exceptions.ReadTimeout,
			botocore.exceptions.EndpointConnectionError) as e:
			#
			#if we get a timeout, retry until we hit max_retries
			#

			logger.error('got a timeout for %s -> %s', objKey, e)
			
			#
			#calculate and print how long it took for this exception to be raised
			# note: this is how you will know what impact changing read_timeout & session_timeout has
			#
			local_elapsed_time = time.time() - local_start_time
			print "this timeout took %s , initiating retry" %(local_elapsed_time)

			#
			#retry until we either succeed, or reach max_retries
			#
			for attempt in range(max_retries):
				#
				#exponential backoff
				#

				#use 30 seconds as the minimum backoff

				backoff = (2 ** attempt) * 30
				print "sleeping for %s secs before retry" %(backoff) 
				time.sleep(backoff)

				print "attempt #%s of %s" %(attempt + 1,max_retries)
				try:
					response =  transfer.upload_file(
						input_file, 
						bucket,
						objKey
						)
				
					local_elapsed_time = time.time() - local_start_time
					print "at %s made file # %s in %s" %(nowtime, i, local_elapsed_time)
					break
				except (botocore.vendored.requests.exceptions.ConnectionError, 
						botocore.vendored.requests.exceptions.ReadTimeout,
						botocore.exceptions.EndpointConnectionError) as e:
					if attempt < (max_retries - 1):
						logger.error('attempt %s for %s failed with %s, %s remaining', attempt + 1, objKey,e,max_retries - attempt)
						continue
					else:
						logger.error('All %s attempts for %s failed, aborting this file',max_retries,objKey)
						break

	global_elapsed_time = time.time() - global_start_time
	print "Done making %s files, it took %s" %(filecount, global_elapsed_time)



def delete_object(s3client,bucket,objKey):
	method = 'delete_object'
	
	try:
		response = s3client.delete_object(
		    Bucket=bucket,
		    Key=objKey
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)




#########
#end of functions
#########


if __name__ == '__main__':
	main()



