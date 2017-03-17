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



prefix = 'http://'


#
# end of variables
##################


print_verbose = False
use_ssl = False
#
#set tests == 'all' as a default
#

#
#provide some CLI options.  If they aren't set, we assume
# variables in the previous section are to be used.
#

try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:a:s:ub:t:vo:", ["host=","port=","access_key=",
        	"secret_key=","use_ssl","bucket=","tests=","verbose"])
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
	if opt in ('-o','--objectkey'):
		objKey = arg




#####
#only use the hardcoded options if we didn't get any passed to us.
#


if len(opts) < 4:
	print "syntax is `./s3_boto3_basic_tests.py -h <hostname> -p 80 -a <access_key> -s <secret_key> -b <bucket> -o objectKey`"
	sys.exit(1)






def make_session():

	session = boto3.session.Session()


	s3client = session.client('s3',
			aws_access_key_id = access_key,
	        aws_secret_access_key = secret_key,
			endpoint_url= host + ':' + port,
			#region_name is needed for s3v4. can be pretend.
			region_name="iggy-1",
			use_ssl=False,
			verify=False,
			config=boto3.session.Config(
				#set signature_version to either s3 or s3v4
				#note: if you set to s3v4 you need to set a 'region_name'
				#important: s3v4 will cause PUTs of objects to fail..for now.
				signature_version='s3',
				connect_timeout=60,
				read_timeout=60,
				#addressing style must be set to 'path'
				s3={'addressing_style': 'path'})
			)

	return s3client





def list_object_versions(bucket,objKey):
	#this is another bucket op
	method = 'list_object_versions'

	try:
		response = s3client.list_object_versions(
	    Bucket=bucket,
		Prefix=objKey
		)
		return response
	except botocore.exceptions.ClientError as e:
		print "error: %s" %(e)
		sys.exit(1)





def head_object(bucket,objKey):
	method = 'head_object'
	try:
		response = s3client.head_object(
			Bucket=bucket,
			Key=objKey)
		printsuccess(method,response)

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		printfail(method,e.response)


def restore_object(bucket,objKey):
	#
	#note: we do have versions, but i'll just see how we handle request
	# before i put a 'real' archived version in here
	#
	method = 'restore_object'

	try:
		response = s3client.restore_object(
			Bucket=bucket,
		    Key=objKey,
		    VersionId='1',
		    RequestPayer='requester'
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)



def delete_object(bucket,objKey,vers_to_del):
	method = 'delete_object'

	try:
		response = s3client.delete_object(
		    Bucket=bucket,
		    Key=objKey,
			VersionId=vers_to_del
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)







#########
#end of functions
#########

s3client = make_session()
objInfo = list_object_versions(bucket,objKey)
print objInfo
