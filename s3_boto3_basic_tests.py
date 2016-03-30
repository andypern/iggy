#!/usr/bin/env python

import boto3
import botocore

from datetime import datetime
import time
import os
import sys
import getopt
import re
from string import ascii_uppercase
from random import choice




#TODO: 


# * make a way to specify which tests you want to run, eg:
# - --tests put_bucket_acl,put_object_acl , etc
# * make a flag that runs all tests, instead of hand-calling them
# * 



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
	except ClientError as e:
		print e.message
		sys.exit(0)

	
	#print len(response['Buckets'])

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

	#HEAD first :)  this fails if we don't set an acl at create time
	try:
		s3client.head_bucket(Bucket=cName)
	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		print e.response


def get_bucket_acl(cName):
	#get the bucket acl
	print "+++++++++++++++++"
	try:
		acl = s3client.get_bucket_acl(
			Bucket=cName)
		print acl

	except botocore.exceptions.ClientError as e:
		print e.response

def list_objects(cName):		 
	#list what's inside
	print "+++++++++++++++++"
	try:
		objList = s3client.list_objects(
			Bucket=cName,
			MaxKeys=100)
		print objList
	except botocore.exceptions.ClientError as e:
		print e.response





def get_slew_bucket_ops(cName):
	
	#
	#slew of bucket operations packed into a single function for now
	#

	#first, build a list of methods
	print "+++++++++++++++++"
	method_list = dir(s3client)
	# we'll want a regex to filter for the ones we want.
	get_bucket_Re = re.compile('^get_bucket')
	

	for method in method_list:
		if get_bucket_Re.match(method):
			print method
			callable_method = getattr(s3client, method)
			try:
				response = callable_method(
					Bucket=cName
					)
				print response
			except botocore.exceptions.ClientError as e:
				print e.response

def list_multipart_uploads(cName):
	#this is actually a bucket level op
	print '+++list_multipart_uploads+++'

	try:
		response = s3client.list_multipart_uploads(
	    Bucket=cName
		)
		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def list_object_versions(cName):
	#this is another bucket op
	print '+++list_object_versions+++'

	try:
		response = s3client.list_object_versions(
	    Bucket=cName
		)
		print response
	except botocore.exceptions.ClientError as e:
		print e.response


#
# Bucket put ops .  Can't quite iterate through like we did with
# the 'gets'.  So...here goes..
#


def put_bucket_acl(cName):
	print '+++put_bucket_acl+++'
	
	try:
		response = s3client.put_bucket_acl(
			ACL='private',
			Bucket=cName
			)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_cors(cName):
	print '+++put_bucket_cors+++'
	
	try:
		response = s3client.put_bucket_cors(
		    Bucket=cName,
		    CORSConfiguration={
		        'CORSRules': [
		            {
		                'AllowedHeaders': [
		                    'string',
		                ],
		                'AllowedMethods': [
		                    'PUT','GET','POST','HEAD','DELETE',
		                ],
		                'AllowedOrigins': [
		                    '*',
		                ],
		                'ExposeHeaders': [
		                    'string',
		                ],
		                'MaxAgeSeconds': 123
		            },
		        ]
		    },

		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response



def put_bucket_lifecycle_configuration(cName):
	print '+++put_bucket_lifecycle_configuration+++'
	
	try:
		response = s3client.put_bucket_lifecycle_configuration(
    Bucket=cName,
    LifecycleConfiguration={
        'Rules': [
            {
                'Expiration': {
                    'Date': datetime(2015, 1, 1),
                    'Days': 123,
                    'ExpiredObjectDeleteMarker': True|False
                },
                'ID': 'configrule',
                'Prefix': 'logs/',
                'Status': 'Enabled',
                'Transitions': [
                    {
                        'Date': datetime(2015, 1, 1),
                        'Days': 123,
                        'StorageClass': 'STANDARD_IA'
                    },
                ],
                'NoncurrentVersionTransitions': [
                    {
                        'NoncurrentDays': 123,
                        'StorageClass': 'STANDARD_IA'
                    },
                ],
                'NoncurrentVersionExpiration': {
                    'NoncurrentDays': 123
                },
                'AbortIncompleteMultipartUpload': {
                    'DaysAfterInitiation': 123
                }
            },
        ]
    }
)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_logging(cName):
	print '+++put_bucket_logging+++'
	
	try:
		response = s3client.put_bucket_logging(
		    Bucket=cName,
		    BucketLoggingStatus={
		        'LoggingEnabled': {
		            'TargetBucket': cName,
		            'TargetGrants': [
		                {
		                    'Grantee': {
		                        'DisplayName': 'iggy',
		                        'EmailAddress': 'iggy@igneous.io',
		                        'ID': 'iggyID',
		                        'Type': 'CanonicalUser'
		                    },
		                    'Permission': 'FULL_CONTROL'
		                },
		            ],
		            'TargetPrefix': 'logs/'
		        }
		    },
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response




def put_bucket_notification_configuration(cName):
	print '+++put_bucket_notification_configuration+++'
	
	try:
		response = s3client.put_bucket_notification_configuration(
		    Bucket=cName,
		    NotificationConfiguration={}
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_policy(cName):
	print '+++put_bucket_policy+++'
	
	try:
		response = s3client.put_bucket_policy(
		    Bucket=cName,
		    Policy='string'
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_replication(cName):
	print '+++put_bucket_replication+++'
	
	try:
		response = s3client.put_bucket_replication(
		    Bucket=cName,
		    ReplicationConfiguration={
		        'Role': 'IAM-Role-ARN',
		        'Rules': [
		            {
		                'ID': 'Rule-1',
		                'Prefix': 'logs/',
		                'Status': 'Enabled',
		                'Destination': {
		                    'Bucket': cName,
		                    'StorageClass': 'STANDARD'
		                }
		            },
		        ]
		    }
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_request_payment(cName):
	print '+++put_bucket_request_payment+++'
	
	try:
		response = s3client.put_bucket_request_payment(
		    Bucket=cName,
		    RequestPaymentConfiguration={
		        'Payer': 'BucketOwner'
		    }
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_tagging(cName):
	print '+++put_bucket_tagging+++'
	
	try:
		response = s3client.put_bucket_tagging(
		    Bucket=cName,
		    Tagging={
		        'TagSet': [
		            {
		                'Key': 'andyp',
		                'Value': 'is_cool'
		            },
		        ]
		    }
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_versioning(cName):
	print '+++put_bucket_versioning+++'
	
	try:
		response = s3client.put_bucket_versioning(
		    Bucket=cName,
		    VersioningConfiguration={
		        'MFADelete': 'Enabled',
		        'Status': 'Enabled'
		    }
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_bucket_website(cName):
	print '+++put_bucket_website+++'
	
	try:
		response = s3client.put_bucket_website(
		    Bucket=cName,
		    WebsiteConfiguration={
		        'ErrorDocument': {
		            'Key': 'error_page.html'
		        },
		        'IndexDocument': {
		            'Suffix': 'index.html'
		        },
		        'RedirectAllRequestsTo': {
		            'HostName': 'www.iggy.bz',
		            'Protocol': 'http'
		        },
		    }
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response



#
#
#
####end of bucket ops####


####Start of object Ops####
#
#
#

#
#Object get ops
#


def get_slew_object_ops(cName,objKey):
	#first lets build and print out the list of avail ops

	print "+++++++++++++++++"
	method_list = dir(s3client)
	# we'll want a regex to filter for the ones we want.
	get_bucket_Re = re.compile('^get_object')
	

	for method in method_list:
		if get_bucket_Re.match(method):
			print method
			callable_method = getattr(s3client, method)
			try:
				response = callable_method(
					Bucket=cName,
					Key=objKey
					)
				print response
			except botocore.exceptions.ClientError as e:
				print e.response



def head_object(cName,objKey):
	print "+++++++++++++++++"
	try:
		response = s3client.head_object(
			Bucket=cName,
			Key=objKey)
		print response

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		print e.response

def list_parts(cName,objKey):
	#this is probably only valid if there are any multi-part uploads
	# but it seems to work (empty list)

	print "+++list_parts(%s , %s)+++" %(cName,objKey)
	try:
		response = s3client.list_parts(
			Bucket=cName,
			Key=objKey,
			UploadId='xyz')
		print "ran"
		#print response

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		print e.response
	except botocore.parsers.ResponseParserError as e:
		print 'parser error: %s' %(e)


#
#puts
#

def put_object_basic(cName):
	#
	#basic object put, nothing special
	#
	print "+++++++++++++++++"
	objKey = "file-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.put_object(
			Body=b'xyz',
			Bucket=cName,
			Key=objKey)
		print response
		return objKey
	except botocore.exceptions.ClientError as e:
		print e.response


def put_object_with_acl(cName):
	#
	#put another object, this time force the ACL to be set
	#
	print "+++++++++++++++++"
	objKey = "file-acl-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.put_object(
			ACL='private',
			Body=b'xyz',
			Bucket=cName,
			Key=objKey)
		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def put_object_acl(objKey,cName):
	#
	#slightly different, we need to do this against an existing object
	#
	print "+++++++++++++++++"

	try:
		response = s3client.put_object_acl(
			ACL='private',
			AccessControlPolicy={
		        'Grants': [
		            {
		                'Grantee': {
		                    'DisplayName': 'dorkface',
		                    'EmailAddress': 'dork@dork.com',
		                    'Type': 'CanonicalUser',
		                    'ID': 'apkey'
		                },
		                'Permission': 'FULL_CONTROL'
		            },
		        ],
		        'Owner': {
		            'DisplayName': 'igneous',
		            'ID': 'igneous'
		        }
		    },
			Bucket=cName,
			Key=objKey)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def restore_object(cName,objKey):
	#
	#note: we do have versions, but i'll just see how we handle request 
	# before i put a 'real' archived version in here
	#
	print "+++++++++++++++++"
	
	try:
		response = s3client.restore_object(
			Bucket=cName,
		    Key=objKey,
		    VersionId='1',
		    RequestPayer='requester'
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def upload_file(cName):
	#
	try:
		response = s3client.upload_file(
			'/tmp/hello.txt', 
			cName,
			'hello.txt'
			)
		print response
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
#cName = create_bucket()
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




# head_bucket(cName)
# put_bucket_acl(cName)
# get_bucket_acl(cName)
# put_bucket_cors(cName)
# put_bucket_lifecycle_configuration(cName)
# put_bucket_logging(cName)
# put_bucket_notification_configuration(cName)
# put_bucket_policy(cName)
# put_bucket_replication(cName)
# put_bucket_request_payment(cName)
# put_bucket_tagging(cName)
# put_bucket_versioning(cName)
# put_bucket_website(cName)


#objKey = put_object_basic(cName)
#print objKey

#get_slew_bucket_ops(cName)
#list_multipart_uploads(cName)
#list_object_versions(cName)
#list_objects(cName)
#list_parts(cName,objKey)
#restore_object(cName,objKey)
upload_file(cName)




#put_object_with_acl(cName)
#put_object_acl(objKey,cName)


#get_slew_object_ops(cName,objKey)
#head_object(cName,objKey)












