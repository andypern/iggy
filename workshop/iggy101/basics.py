#!/usr/bin/env python

import boto3
import botocore

from datetime import datetime
import time
import os
import sys





#
#here's how to form a connection object
#
def make_iggy_session(endpoint,iggy_key,iggy_secret,use_ssl):

	iggySession = boto3.session.Session()

	iggyClient = iggySession.client('s3',
			aws_access_key_id = iggy_key,
	        aws_secret_access_key = iggy_secret,
			endpoint_url=endpoint,
			config=boto3.session.Config(
				signature_version='s3',
				connect_timeout=60,
				read_timeout=60,
				s3={'addressing_style': 'path'})
			)

	return iggyClient


def list_buckets(client):
    """
    Return a generator that iterates through the buckets in the root container.
    """

    
    lsb_resp = client.list_buckets()

    for bucket in lsb_resp['Buckets']:
        yield bucket['Name']



def list_objects(s3Client,bucket):
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







if __name__ == "__main__":




	iggyClient = make_iggy_session(endpoint,key,secret,use_ssl)




	objPages = list_objects(iggyClient,bucket)


	for page in objPages:
		for key in page['Contents']:
			objKey =  key['Key']
			#print objKey
			objList.append(objKey)


	end_time = time.time()

	total_time = end_time - start_time
	print "len: %s, time: %s" %(len(objList),total_time)
