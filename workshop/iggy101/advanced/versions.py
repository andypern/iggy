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
import logging

import json

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



def list_object_versions(cName):
	#this is another bucket op
	method = 'list_object_versions'

	try:
		response = s3client.list_object_versions(
	    Bucket=cName
		)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)


def head_object(cName,objKey):
	method = 'head_object'
	try:
		response = s3client.head_object(
			Bucket=cName,
			Key=objKey)
		printsuccess(method,response)

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		printfail(method,e.response)
