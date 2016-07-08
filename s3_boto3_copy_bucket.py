#!/usr/bin/env python

import boto3
import botocore
from boto3.s3.transfer import S3Transfer, TransferConfig

import xml.etree
import pprint
from datetime import datetime
import time
import os
import sys
import ConfigParser
import argparse
import re
from string import ascii_uppercase
from random import choice
import threading
import Queue
import logging

import json






#TODO: 

# * threading
# * limit queue to not run out of RAM?
	# * perhaps do this based on content-length
# * deal with metadata
# implement logging



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

def make_aws_session(s3_key,s3_secret):

	s3Session = boto3.session.Session()

	s3Client = s3Session.client('s3',
			aws_access_key_id = s3_key,
	        aws_secret_access_key = s3_secret
			)

	return s3Client



def check_buckets(iggyClient,s3Client,src_bucket,dest_bucket):

	try:
		iggyBucket = iggyClient.head_bucket(Bucket=dest_bucket)
	
	except botocore.exceptions.ClientError as e:
		#print dir(e)
		print "had an issue with dest_bucket : %s , %s" %(dest_bucket,e.response)
		sys.exit(1)
		#error_code = int(e.response['Error']['Code'])

	try:
		s3Bucket = s3Client.head_bucket(Bucket=src_bucket)
	except botocore.exceptions.ClientError as e:
		#print dir(e)
		print "had an issue with src_bucket : %s , %s" %(src_bucket,e.response)
		sys.exit(1)
		#error_code = int(e.response['Error']['Code'])
 
	return iggyBucket,s3Bucket
	



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


		#printsuccess(method,paginator)
		return pages
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)



def get_key(s3Client,src_bucket,objKey):
	try:
		response = s3Client.get_object(
			Bucket=src_bucket,
			Key=objKey)
		return response

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		print error_code



def put_key(iggyClient,dest_bucket,keyDict,objKey,prefix):
	

	putKey = prefix + "/" + objKey
	try:
		response = iggyClient.put_object(
			Body=keyDict['Body'].read(),
			Bucket=dest_bucket,
			Key=putKey)
		return response
	
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)



def put_object_lots(cName):
	method = 'put_object_lots'
	keyCount = 1000
	for i in range(keyCount):
		objKey = "file-" + '-' + str(i) + '-' + (''.join(choice(ascii_uppercase) for i in range(3))) 
		try:
			response = s3client.put_object(
			Body=b'xyz',
			Bucket=cName,
			Key=objKey)
			printsuccess(method,response)
		except botocore.exceptions.ClientError as e:
			printfail(method,e.response)
	print "Done making %s files" %(keyCount)




def upload_file(cName):
	method = 'upload_file'
	objKey = "upload-" + (''.join(choice(ascii_uppercase) for i in range(6))) + '.txt'

	try:
		response = s3client.upload_file(
			'/tmp/hello.txt', 
			cName,
			objKey
			)
		printsuccess(method,response)
		return objKey
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)





#########
#end of functions
#########


if __name__ == "__main__":


	parser = argparse.ArgumentParser(description = "s3 bucket to bucket copy")

	parser.add_argument('-v', '--verbose',
	help="Verbose output",
	required = False,
	action = 'store_true',
	default = False)
	parser.add_argument('-q', '--quiet',
	help="No output",
	required = False,
	action = 'store_true',
	default = False)

	parser.add_argument('-t', '--thread-count',	
	help='Number of worker threads processing the objects',
	dest='threads_no',
	required = False,
	type = int,
	default = 20)

	parser.add_argument('-', '--prefix',	
	help='directory on target to put data into, default is bucketBackup',
	dest='prefix',
	required = False,
	default = 'bucketBackup')

	parser.add_argument('--src_bucket', 
	help = "Source s3 bucket name and optional path")

	parser.add_argument('--dest_bucket',
	help = "Destination s3 bucket name")

	parser.add_argument('--iggy_key',
	help = "Igneous access key")

	parser.add_argument('--s3_key',
	help = "amazon s3 access key")

	parser.add_argument('--iggy_secret',
	help = "Igneous secret key")

	parser.add_argument('--s3_secret',
	help = "s3 secret key")

	parser.add_argument('-e', '--endpoint',
	help = "Igneous endpoint, eg: http://igneous.company.com:80")

	args =  parser.parse_args()
	

	if args.quiet:
		args.verbose = False


	iggyClient = make_iggy_session(args.endpoint,args.iggy_key,args.iggy_secret)
	s3Client = make_aws_session(args.s3_key,args.s3_secret)


	iggyBucket,s3Bucket = check_buckets(iggyClient,s3Client,args.src_bucket,args.dest_bucket)

	objPages = list_objects(s3Client,args.src_bucket)


	for page in objPages:
	 	for key in page['Contents']:
	 		objKey =  key['Key']
	 		getResponse = get_key(s3Client,args.src_bucket,objKey)
	 		#for myKey in getResponse.keys():
	 		#	print myKey
	 		putResponse = put_key(iggyClient,args.dest_bucket,getResponse,objKey,arg.prefix)
	 		print putResponse







