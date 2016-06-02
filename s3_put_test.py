#!/usr/bin/env python

import boto3
import botocore

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



########
#This is a script to put a bunch of dummy files into a a bucket.
#Use case is primarily to run tests during a planned outage such as a Petra & Lithos upgrade.
#Boto3 has some logic around retries and timeouts, but we also have to handle 500 errors
#which get returned by the server when S3liteD is UP, but some lithos are down.
#

#TODO: 

# * breakout retry logic into a function to eliminate dupliation
# * rename this file and add in a download/read function
# * trap and handle 500 errors

###############
# some variables , will make this dynamic in the future.
#
urlprefix = 'http://'

#random file prefix so we can clean up easily also

fileprefix = "file-"


#
#set defaults, can be overriden via args
#

print_verbose = False
largeFiles = False
delete_only = False
filecount = 1000
session_timeout = 1
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
        opts, args = getopt.getopt(sys.argv[1:], "h:p:a:s:b:c:dlr:v", 
        	["host=","port=","access_key=","secret_key=","bucket=","count=",
        	"delete","large","retries=","verbose"])
except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print "wrong option"
        sys.exit(2)


for opt, arg in opts:

	if opt in ('-h', '--host'):
		host = arg
	if opt in ('-p', '--port'):
		port = arg
	if opt in ('-a', '--access_key'):
		access_key = arg
	if opt in ('-s','--secret_key'):
		secret_key = arg
	if opt in ('-b','--bucket'):
		bucket = arg
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
#we require 5 arg's, and 2 are optional.
#

if len(opts) < 5:
	print "syntax is `./s3_put_test.py -h <hostname> -p 80 -a <access_key> -s <secret_key> -b bucket [-c filecount] [--delete] [--large] [-r retries] [--verbose]`"
	sys.exit(1)







def printfail(method,response):
	#
	#this is mainly so we have a consistent way to print 
 	#
 	# for later: if there is the '-v' flag set by the user, print more verbose stuff.
 	#
 	if print_verbose == True:
 		print "%s,%s" % (method,response)
 	else:
		print "%s,%s" % (method,response['ResponseMetadata']['HTTPStatusCode'])


def printsuccess(method,response):
	#
	#this is mainly so we have a consistent way to print
 	#
 	# for later: if there is the '-v' flag set by the user, print more verbose stuff.
 	#
 	if print_verbose == True:
 		print "%s,%s" % (method,response)
 	else:
 		try:	
	 		print "%s,%s" % (method,response['ResponseMetadata']['HTTPStatusCode'])
 		except TypeError as e:
 			print "%s : 200 , but had TypeError : %s" %(method,e)



	#
	#build the client session.  Note the signature version
	# is required to be 's3' at this time, as opposed to 's3v4'
	#

def make_session():

	session = boto3.session.Session()

	s3client = session.client('s3',
			aws_access_key_id = access_key,
	        aws_secret_access_key = secret_key,
			endpoint_url=urlprefix + host + ':' + port,
			use_ssl=False,
			verify=False,
			config=boto3.session.Config(
				signature_version='s3',
				connect_timeout=session_timeout,
				read_timeout=session_timeout,
				s3={'addressing_style': 'path'})
			)

	return s3client



######Functions#####
#
#
#


def list_objects(bucket, fileprefix):		 
	#
	#note that you can only get back up to 1000 keys at a time
	# so using pagination to try and get them all.
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







def put_object_lots(bucket, filecount, fileprefix):
	method = 'put_object_lots'
	global_start_time = time.time()
	for i in range(filecount):
		local_start_time = time.time()
		nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
		objKey = fileprefix + '-' + str(i) + '-' + (''.join(choice(ascii_uppercase) for i in range(6))) + '.txt'
		try:
			response = s3client.put_object(
			Body=b'xyz',
			Bucket=bucket,
			Key=objKey)
			#printsuccess(method,response)
			local_elapsed_time = time.time() - local_start_time
			print "at %s made file # %s in %s" %(nowtime, i, local_elapsed_time)
		except botocore.exceptions.ClientError as e:
			printfail(method,e.response)
		except botocore.vendored.requests.exceptions.ReadTimeout as e:
			#if we get a timeout, retry until we hit max_retries

			print "got a timeout for %s: %s" %(objKey,e)
			local_elapsed_time = time.time() - local_start_time
			print "this timeout took %s , initiating retry" %(local_elapsed_time)

			for attempt in range(max_retries):
				print "attempt #%s of %s" %(attempt + 1,max_retries)
				try:
					response = s3client.put_object(
					Body=b'xyz',
					Bucket=bucket,
					Key=objKey)
					#printsuccess(method,response)
					local_elapsed_time = time.time() - local_start_time
					print "at %s made file # %s in %s" %(nowtime, i, local_elapsed_time)
					break
				except botocore.vendored.requests.exceptions.ReadTimeout as e:
					if attempt < (max_retries - 1):
						print "attempt %s failed, %s remaining" %(attempt + 1, max_retries - attempt)
						continue
					else:
						print "all attempts failed..aborting this transfer"
						break

	global_elapsed_time = time.time() - global_start_time
	print "Done making %s files, it took %s" %(filecount, global_elapsed_time)


#
#use this if you want files that are more than just a few bytes
#

def upload_file(bucket, filecount, fileprefix):
	method = 'upload_file'
	global_start_time = time.time()
	for i in range(filecount):
		local_start_time = time.time()
		nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
		objKey = fileprefix + '-' + str(i) + '-' + (''.join(choice(ascii_uppercase) for i in range(6))) + '.2mb'

		try:
			response = s3client.upload_file(
				'/tmp/2mb.file', 
				bucket,
				objKey
				)
			#printsuccess(method,response)
			local_elapsed_time = time.time() - local_start_time
			print "at %s made file # %s in %s" %(nowtime, i, local_elapsed_time)
		except botocore.exceptions.ClientError as e:
			printfail(method,e.response)
		except (botocore.vendored.requests.exceptions.ConnectionError, 
			botocore.vendored.requests.exceptions.ReadTimeout) as e:
			#if we get a timeout, retry until we hit max_retries
			print "got a timeout for %s: %s" %(objKey,e)
			local_elapsed_time = time.time() - local_start_time
			print "this timeout took %s , initiating retry" %(local_elapsed_time)

			for attempt in range(max_retries):
				print "attempt #%s of %s" %(attempt + 1,max_retries)
				try:
					response =  s3client.upload_file(
						'/tmp/2mb.file', 
						bucket,
						objKey
						)
					#printsuccess(method,response)
					local_elapsed_time = time.time() - local_start_time
					print "at %s made file # %s in %s" %(nowtime, i, local_elapsed_time)
					break
				except (botocore.vendored.requests.exceptions.ConnectionError, 
						botocore.vendored.requests.exceptions.ReadTimeout) as e:
					if attempt < (max_retries - 1):
						print "attempt %s failed, %s remaining" %(attempt + 1, max_retries - attempt)
						continue
					else:
						print "all attempts failed..aborting this transfer"
						break

	global_elapsed_time = time.time() - global_start_time
	print "Done making %s files, it took %s" %(filecount, global_elapsed_time)


def delete_object(bucket,objKey):
	method = 'delete_object'
	
	try:
		response = s3client.delete_object(
		    Bucket=bucket,
		    Key=objKey
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)


#
#right now this won't work, need to use the one-at-a-time method
#

def delete_objects(cName,objList):
	method = 'delete_objects'

	objList['Contents'][0]['Key']
	
	try:
		response = s3client.delete_objects(
		    Bucket=cName,
		    Delete={
		        'Objects': [
		            {
		                'Key': objList['Contents'][0]['Key']
		            }
		        ],
		        'Quiet': False
		    },
		)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)



#########
#end of functions
#########

s3client = make_session()

if delete_only == True:
	print "deleting all files starting with %s/%s" %(bucket,fileprefix)
	objList =  list_objects(bucket, fileprefix)
	count = 0
	for page in objList:
		for key in page['Contents']:
			delete_object(bucket,key['Key'])
			count += 1
	print "deleted %s" %(count)
else:

	print "putting %s files to %s"  %(filecount, bucket)

	if largeFiles == True:
		upload_file(bucket, filecount, fileprefix)

	else:	
		put_object_lots(bucket, filecount, fileprefix)

	print "finished putting %s files" %(filecount)

	#
	#get a list of objects in pages, then blow them away
	#

	objList =  list_objects(bucket, fileprefix)

	count = 0
	for page in objList:
			for key in page['Contents']:
				delete_object(bucket,key['Key'])
				count += 1


	print "deleted %s" %(count)





