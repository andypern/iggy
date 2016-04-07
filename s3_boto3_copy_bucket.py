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




#TODO: 



###############
# some variables you will want to set. If not, you need to specify arg's
# see next section
#
prefix = 'http://'

#
# end of variables
##################


print_verbose = False

#
#provide some CLI options.  If they aren't set, we assume
# variables in the previous section are to be used.
#

try:
        opts, args = getopt.getopt(sys.argv[1:], "b:h:p:a:s:v", ["bucket=","host=","port=","access_key=",
        	"secret_key","verbose"])
except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print "wrong option"
        sys.exit(2)


for opt, arg in opts:
	if opt in ('-b', '--bucket'):
		bucket = arg
	if opt in ('-h', '--host'):
		host = arg
	if opt in ('-p', '--port'):
		port = arg
	if opt in ('-a', '--access_key'):
		access_key = arg
	if opt in ('-s','--secret_key'):
		secret_key = arg
	if opt in ('-v', '--verbose'):
		print_verbose = True




#####
#only use the hardcoded options if we didn't get any passed to us. 
#


if len(opts) < 5:
	print "syntax is `./s3_boto3_shortlist.py -h <hostname> -p 80 -a <access_key> -s <secret_key>`"
	sys.exit(1)




def printfail(method,response):
	#
	#this is mainly so we have a consistent way to print shit
 	#
 	# for later: if there is the '-v' flag set by the user, print more verbose stuff.
 	#
 	if print_verbose == True:
 		print "%s,%s" % (method,response)
 	else:
		print "%s,%s" % (method,response['ResponseMetadata']['HTTPStatusCode'])


def printsuccess(method,response):
	#
	#this is mainly so we have a consistent way to print shit
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
	# is required to be 's3' at this time. 
	#

def make_session():

	session = boto3.session.Session()

	s3client = session.client('s3',
			aws_access_key_id = access_key,
	        aws_secret_access_key = secret_key,
			endpoint_url=prefix + host + ':' + port,
			use_ssl=False,
			verify=False,
			config=boto3.session.Config(
				signature_version='s3',
				connect_timeout=60,
				read_timeout=60,
				s3={'addressing_style': 'path'})
			)

	return s3client



######Bucket ops#####
#
#
#

def list_buckets():
	#
	#attempt to list buckets
	#

	try:
		response = s3client.list_buckets()
	except botocore.exceptions.ClientError as e:
		print e.message
		sys.exit(0)

	
	#print len(response['Buckets'])

	return(response)


def create_bucket():

	print "+++create_bucket+++"
	#
	#make a bucket
	#
	# make the container name random
	cName = "test-" + (''.join(choice(ascii_uppercase) for i in range(12)))
	try:
		response = s3client.create_bucket(
			Bucket=cName,
			ACL='public-read-write',
			GrantFullControl='apkey',
			)
		print response
		return cName
	except botocore.exceptions.ClientError as e:
		print e.response




#
# access , list , HEAD bucket we just created
#



def list_objects(cName):		 
	#list what's inside
	method = 'list_objects'
	try:
		objList = s3client.list_objects(
			Bucket=cName,
			MaxKeys=100)
		printsuccess(method,objList)
		return objList
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)




		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)
	except botocore.exceptions.ParamValidationError as e:
		print "%s : error before sending request : %s" % (method,e)






#
#
#
####end of bucket ops####


####Start of object Ops####
#
#
#


#
#puts
#

def put_object_basic(cName):
	#
	#basic object put, nothing special
	#
	method = 'put_object_basic'
	objKey = "file-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.put_object(
			Body=b'xyz',
			Bucket=cName,
			Key=objKey)
		printsuccess(method,response)
		return objKey
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




def copy_object(cName,objKey):
	method = 'copy_object'
	newKey = "copy-object-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	
	try:
		response = s3client.copy_object(
		    Bucket=cName,
		    CopySource={'Bucket': cName, 'Key': objKey, 'VersionId': '1'},
		    Key=newKey
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)
	except xml.etree.cElementTree.ParseError as e:
		print "%s : we got a 200 , but had an error that we couldn't resolve : %s" %(method,e)



#########
#end of functions
#########

s3client = make_session()







