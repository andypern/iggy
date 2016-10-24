#!/usr/bin/env python

import boto3
import botocore

import pprint

import os
import sys
import ConfigParser
import argparse
import re

import json
from string import ascii_uppercase
from random import choice










class Ddict(dict):
	def __init__(self, default=None):
		self.default = default

	def __getitem__(self, key):
		if not self.has_key(key):
			self[key] = self.default()
		return dict.__getitem__(self, key)



def head_object(objKey,s3client,myBucket):
	#print "head_object : %s , %s" %(myBucket,objKey)
	try:
		response = s3client.head_object(
		Bucket=myBucket,
		Key=objKey)

	except botocore.exceptions.ClientError as e:
		#error_blockquote = int(e.response['Error']['blockquote'])
		response = "error"
		return e.response['Error']['Code']
		#print error_blockquote
	except:
		response = "error"
		print "some other error in head_object for %s" %(objKey)
		return "error"

	return response




def make_iggy_session(endpoint,iggy_key,iggy_secret,use_ssl):

	iggySession = boto3.session.Session()

	#print type(iggy_key)
	#print iggy_key
	iggyClient = iggySession.client('s3',
			aws_access_key_id = iggy_key,
	        aws_secret_access_key = iggy_secret,
			endpoint_url=endpoint,
			use_ssl=use_ssl,
			#verify='/usr/local/lib/python2.7/site-packages/botocore/vendored/requests/cacert.pem',
			config=boto3.session.Config(
				signature_version='s3',
				connect_timeout=60,
				read_timeout=60,
				s3={'addressing_style': 'path'})
			)

	return iggyClient



def check_buckets(iggyClient,myBucket):

	try:
		iggyBucket = iggyClient.head_bucket(Bucket=myBucket)

	except botocore.exceptions.ClientError as e:
		#print dir(e)
		print "had an issue with bucket : %s , %s" %(myBucket,e.response)
		return "badBucket"
		#error_blockquote = int(e.response['Error']['blockquote'])


	return iggyBucket


def put_obj_metadata(iggyClient,myBucket,metaDict,objKey):

	kwargs = {}
	kwargs['Bucket'] = myBucket
	kwargs['Key'] = objKey
	kwargs['CopySource'] = {'Bucket': myBucket, 'Key': objKey}
	kwargs['MetadataDirective'] = 'COPY'
	kwargs['Metadata'] = metaDict


	try:
		response = iggyClient.copy_object(**kwargs)
		return response

	except botocore.exceptions.ClientError as e:
		print "error putting %s : %s" %(objKey,e)



def put_object_basic(iggyClient,myBucket,objKey):

	try:
		response = iggyClient.put_object(
			Body=b'xyz',
			Bucket=myBucket,
			Key=objKey,
			Metadata={'foo': 'bar'})
		return objKey
	except botocore.exceptions.ClientError as e:
		print e.response




def getArgs():

	argparser = argparse.ArgumentParser(description = "do music stuff")
	argparser.add_argument('-k', '--key', dest="access_key",
	help = "Igneous access key")


	argparser.add_argument('-s','--secret', dest="secret",
	help = "Igneous secret key")

	argparser.add_argument('-e', '--endpoint',
	help = "Igneous endpoint, eg: http://igneous.company.com:80")

	argparser.add_argument('-b', '--bucket', dest="myBucket",
	help = "bucket")
	argparser.add_argument('-u', '--use_ssl',
	dest='use_ssl',
	default=False,
	help = "use ssl..or not default is not")


	args =  argparser.parse_args()



	return args.endpoint,args.access_key,args.secret,args.use_ssl,args.myBucket





#########
#end of functions
#########


if __name__ == "__main__":
	# get args
	endpoint,access_key,secret,use_ssl,myBucket = getArgs()
	iggyClient = make_iggy_session(endpoint,access_key,secret,use_ssl)

	objKey = "file-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	#first put the file, with basic metadata

	putResp = put_object_basic(iggyClient,myBucket,objKey)

	# see what's there
	objMeta = head_object(objKey,iggyClient,myBucket)



	if "error" in objMeta:
		print "can't proceed"
		sys.exit
	else:
		#print metadata before the next put.
		print objMeta['Metadata']
		#create some new metadata to replace it with.

		metaDict = {}
		metaDict['notfoo'] = 'notbar'

 		#print(json.dumps(beatsDict, indent=2))

		put_result = put_obj_metadata(iggyClient,myBucket,metaDict,objKey)
		#head it again.
		newHead  = head_object(objKey,iggyClient,myBucket)
		print newHead['Metadata']
