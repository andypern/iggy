#!/usr/bin/env python

import boto3
import botocore

import time
import os
import sys
import getopt
from string import ascii_uppercase
from random import choice
from botocore.exceptions import ClientError



###############
# some variables you will want to set. If not, you need to specify arg's
# see next section
#
prefix = 'http://'
slab = "archer"
suffix = ".iggy.bz"
port = "7070"

#
# end of variables
##################



#
#provide some CLI options.  If they aren't set, we assume
# variables in the previous section are to be used.
#

try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:a:s:", ["host=","port=","access_key=",
        	"secret_key"])
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



#####
#only use the hardcoded options if we didn't get any passed to us. 
#


if len(opts) < 4:

	#
	# I setup my environment variables (eg: in .bashrc/.zshrc) 
	# such that I have a 'archer_ACCESS_KEY' etc
	#
	access_key =  os.environ.get(slab + "_ACCESS_KEY", None)
	secret_key = os.environ.get(slab + "_SECRET_KEY", None)
	host = slab + suffix





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





def list_buckets():
	#
	#attempt to list buckets
	#

	print 'list time'
	print s3client

	try:
		response = s3client.list_buckets()
	except ClientError as e:
		print e.message
		sys.exit(0)

	
	print len(response['Buckets'])

	return(response)


def create_bucket():


	#
	#make a bucket
	#
	# make the container name random
	cName = "test-" + (''.join(choice(ascii_uppercase) for i in range(12)))
	try:
		s3client.create_bucket(
			Bucket=cName,
			ACL='public-read-write',
			GrantFullControl='apkey',
			)
		print "made bucket"
		return cName
	except botocore.exceptions.ClientError as e:
		print e.response


#
# access , list , HEAD bucket we just created
#


def head_bucket(cName):

	print 'head'
	

	
	#HEAD first :)  this fails if we don't set an acl at create time
	try:
		s3client.head_bucket(Bucket=cName)
	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		print error_code
		print e.response


def get_bucket_acl(cName):
	#get the bucket acl

	try:
		acl = s3client.get_bucket_acl(
			Bucket=cName)
		print acl


	except botocore.exceptions.ClientError as e:
		print e.response

def list_objects(cName):		 
	#list what's inside

	try:
		response = s3client.list_objects(
			Bucket=cName,
			MaxKeys=100)
	except botocore.exceptions.ClientError as e:
		print e.response

#########
#end of functions
#########

s3client = make_session()

####
#toggle between these two depending on what you want..
#
#
##This is if you want to operate against
##the bucket you just created..probably won't work due to ACL..
#
cName = create_bucket()
#
#
##this one is if you want to operate against the first 
##bucket in the list (loadgen-bucket typicallly on topo12)
#
cName = list_buckets()['Buckets'][0]['Name']
print cName
#
#
#####

#time.sleep(10)


head_bucket(cName)
get_bucket_acl(cName)
list_objects(cName)

#get ACL

#TODO: 


# * put to a bucket/key
# * get from a bucket/key
# * get info from an object
# * get acl on an object
# * 
# * check acl on bucket
# * create bucket with acl
# * overlay acl












