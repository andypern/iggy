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

	parser = argparse.ArgumentParser(description = "list a bucket")



	parser.add_argument('--bucket', dest="bucket",
	help = "bucket to index")


	parser.add_argument('-k', '--key', dest="key",
	help = "Igneous access key")


	parser.add_argument('-s','--secret', dest="secret",
	help = "Igneous secret key")

	parser.add_argument('-e', '--endpoint',
	help = "Igneous endpoint, eg: http://igneous.company.com:80")


	args =  parser.parse_args()



	return args.endpoint,args.bucket,args.key,args.secret







if __name__ == "__main__":


	start_time = time.time()
	objList = []

	endpoint,bucket,key,secret = getArgs()



	iggyClient = make_iggy_session(endpoint,key,secret)




	objPages = list_objects(iggyClient,bucket)


	for page in objPages:
		for key in page['Contents']:
			objKey =  key['Key']
			#print objKey
			objList.append(objKey)


	end_time = time.time()

	total_time = end_time - start_time
	print "len: %s, time: %s" %(len(objList),total_time)


