#!/usr/bin/env python

import boto3

import os
import sys
from botocore.exceptions import ClientError

session = boto3.session.Session()


slab = "archer"
access_key =  os.environ.get(slab + "_ACCESS_KEY", None)
secret_key = os.environ.get(slab + "_SECRET_KEY", None)




s3client = session.client('s3',
		aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
		endpoint_url='http://' + slab + '.iggy.bz:7070',
		config=boto3.session.Config(signature_version='s3')
		)


try:
	response = s3client.list_buckets()
except ClientError as e:
	print e.message
	sys.exit(0)

print response['Buckets']
