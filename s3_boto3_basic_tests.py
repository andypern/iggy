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

# * make a way to specify which tests you want to run, eg:
# - --tests put_bucket_acl,put_object_acl , etc
# * make a flag that runs all tests, instead of hand-calling them
# * figure out how to get the full responses for successes (eg: payload of get_bucket_acl , etc)



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
#set tests == 'all' as a default
#
tests = "all"

#
#provide some CLI options.  If they aren't set, we assume
# variables in the previous section are to be used.
#

try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:a:s:t:v", ["host=","port=","access_key=",
        	"secret_key=","tests=","verbose"])
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
	if opt in ('-t','--tests'):
		tests = arg
	if opt in ('-v', '--verbose'):
		print_verbose = True




#####
#only use the hardcoded options if we didn't get any passed to us. 
#


if len(opts) < 4:
	print "syntax is `./s3_boto3_basic_tests.py -h <hostname> -p 80 -a <access_key> -s <secret_key> [-t tests] [--verbose]`"
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


def head_bucket(cName):

	method = "HEAD Bucket"
	#HEAD first :)  this fails if we don't set an acl at create time
	try:
		response = s3client.head_bucket(Bucket=cName)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		#print dir(e)
		#print e.response
		#error_code = int(e.response['Error']['Code'])
		printfail(method,e.response)


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





def get_slew_bucket_ops(cName):
	
	#
	#slew of bucket operations packed into a single function for now
	#

	#first, build a list of methods
	method_list = dir(s3client)
	# we'll want a regex to filter for the ones we want.
	regex = re.compile('^get_bucket')
	

	for method in method_list:
		if regex.match(method):
			callable_method = getattr(s3client, method)
			try:
				response = callable_method(
					Bucket=cName
					)
				#print "%s , %s" %(method,response)
				printsuccess(method,response)
			except botocore.exceptions.ClientError as e:
				printfail(method,e.response)

def list_multipart_uploads(cName):
	#this is actually a bucket level op
	method = 'list_multipart_uploads'

	try:
		response = s3client.list_multipart_uploads(
	    Bucket=cName
		)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

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


#
# Bucket put ops .  Can't quite iterate through like we did with
# the 'gets'.  So...here goes..
#


def put_bucket_acl(cName):
	method = 'put_bucket_acl'
	try:
		response = s3client.put_bucket_acl(
			ACL='private',
			Bucket=cName
			)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_bucket_cors(cName):
	method = 'put_bucket_cors'
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

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)



def put_bucket_lifecycle_configuration(cName):
	method = 'put_bucket_lifecycle_configuration'
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

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)
	except botocore.exceptions.ParamValidationError as e:
		print "%s : error before sending request : %s" % (method,e)

def put_bucket_logging(cName):
	method = 'put_bucket_logging'
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

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)




def put_bucket_notification_configuration(cName):
	method = 'put_bucket_notification_configuration'
	try:
		response = s3client.put_bucket_notification_configuration(
		    Bucket=cName,
		    NotificationConfiguration={}
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_bucket_policy(cName):
	method = 'put_bucket_policy'
	try:
		response = s3client.put_bucket_policy(
		    Bucket=cName,
		    Policy='string'
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_bucket_replication(cName):
	method = 'put_bucket_replication'
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

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_bucket_request_payment(cName):
	method = 'put_bucket_request_payment'
	try:
		response = s3client.put_bucket_request_payment(
		    Bucket=cName,
		    RequestPaymentConfiguration={
		        'Payer': 'BucketOwner'
		    }
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_bucket_tagging(cName):
	method = 'put_bucket_tagging'
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

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_bucket_versioning(cName):
	method = 'put_bucket_versioning'
	
	try:
		response = s3client.put_bucket_versioning(
		    Bucket=cName,
		    VersioningConfiguration={
		        'MFADelete': 'Enabled',
		        'Status': 'Enabled'
		    }
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_bucket_website(cName):
	method = 'put_bucket_website'
	
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

		print(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def delete_slew_bucket_ops(cName):
	
	#
	#slew of bucket operations packed into a single function for now
	#

	#first, build a list of methods
	method_list = dir(s3client)
	# we'll want a regex to filter for the ones we want.
	regex = re.compile('^delete_bucket')
	

	for method in method_list:
		if regex.match(method):
			callable_method = getattr(s3client, method)
			try:
				response = callable_method(
					Bucket=cName
					)
				printsuccess(method,response)
			except botocore.exceptions.ClientError as e:
				printfail(method,e.response)




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

	method_list = dir(s3client)
	# we'll want a regex to filter for the ones we want.
	regex = re.compile('^get_object')
	

	for method in method_list:
		if regex.match(method):
			print method
			callable_method = getattr(s3client, method)
			try:
				response = callable_method(
					Bucket=cName,
					Key=objKey
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

def list_parts(cName,objKey):
	#this is probably only valid if there are any multi-part uploads
	# but it seems to work (empty list)
	method = 'list_parts'
	#print "+++list_parts(%s , %s)+++" %(cName,objKey)
	try:
		response = s3client.list_parts(
			Bucket=cName,
			Key=objKey,
			UploadId='xyz')
		printsuccess(method,response)
		#print response

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		printfail(method,e.response)
	except botocore.parsers.ResponseParserError as e:
		print '%s : parser error: %s' %(method,e)


def download_file(cName,objKey):
	method = 'download_file'
	try:
		response = s3client.download_file(
			Bucket=cName,
			Key=objKey,
			Filename='/tmp/goodbye.txt')
		printsuccess(method,response)


	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		printfail(method,e.response)

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


def put_object_with_acl(cName):
	#
	#put another object, this time force the ACL to be set
	#
	method = 'put_object_with_acl'
	objKey = "file-acl-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.put_object(
			ACL='private',
			Body=b'xyz',
			Bucket=cName,
			Key=objKey)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def put_object_acl(cName,objKey):
	#
	#slightly different, we need to do this against an existing object
	#
	method = 'put_object_acl'

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

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

def restore_object(cName,objKey):
	#
	#note: we do have versions, but i'll just see how we handle request 
	# before i put a 'real' archived version in here
	#
	method = 'restore_object'
	
	try:
		response = s3client.restore_object(
			Bucket=cName,
		    Key=objKey,
		    VersionId='1',
		    RequestPayer='requester'
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)

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


def create_multipart_upload(cName):
	method = 'create_multipart_upload'
	objKey = "multipart-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.create_multipart_upload(
	    Bucket=cName,
	    Key=objKey,
	)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)


def upload_part(cName):
	method = 'upload_part'
	objKey = "multipart-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.upload_part(
		    Body=b'randombytes',
		    Bucket=cName,
		    Key='fake_file',
		    PartNumber=2,
		    UploadId='1234',
		)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)




def upload_part_copy(cName,objKey):
	method = 'upload_part_copy'
	newKey = "multipart-copy-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.upload_part_copy(
	        Bucket=cName,
		    CopySource={'Bucket': cName, 'Key': objKey, 'VersionId': '1'},
		    Key=newKey,
		    PartNumber=1,
		    UploadId='12345'
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)
	except xml.etree.cElementTree.ParseError as e:
		print " %s : we got a 200 , but had an error that we couldn't resolve : %s" %(method,e)




def abort_multipart_upload(cName,objKey):
	method = 'abort_multipart_upload'
	
	try:
		response = s3client.abort_multipart_upload(
		    Bucket=cName,
		    Key=objKey,
		    UploadId='1234',
		    RequestPayer='requester'
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)



def complete_multipart_upload(cName,objKey):
	method = 'complete_multipart_upload'	
	try:
		response = s3client.complete_multipart_upload(
		    Bucket=cName,
		    Key=objKey,
		    UploadId='1234'
		)

		printsuccess(method,response)
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


def delete_object(cName,objKey):
	method = 'delete_object'
	
	try:
		response = s3client.delete_object(
		    Bucket=cName,
		    Key=objKey
		)

		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)




def delete_objects(cName,objList):
	method = 'delete_objects'

	objList['Contents'][0]['Key']
	
	try:
		response = s3client.delete_objects(
		    Bucket=cName,
		    Delete={
		        'Objects': [
		            {
		                'Key': objList['Contents'][0]['Key']
		            }
		        ],
		        'Quiet': False
		    },
		)
		printsuccess(method,response)
	except botocore.exceptions.ClientError as e:
		printfail(method,e.response)


#
#this is ugly, for now.
#

def tests_all(cName):

	head_bucket(cName)
	put_bucket_acl(cName)
	get_slew_bucket_ops(cName)


	put_bucket_cors(cName)
	put_bucket_lifecycle_configuration(cName)
	put_bucket_logging(cName)
	put_bucket_notification_configuration(cName)
	put_bucket_policy(cName)
	put_bucket_replication(cName)
	put_bucket_request_payment(cName)
	put_bucket_tagging(cName)
	put_bucket_versioning(cName)
	put_bucket_website(cName)


	delete_slew_bucket_ops(cName)


	#########
	#
	#if you want to run any object related things, make sure the following line is
	# uncommented.

	objKey = put_object_basic(cName)
	#print objKey

	#maybe you want to make a lot of files

	#put_object_lots(cName)

	#if you want to delete multiple objects, use this:

	objList = list_objects(cName)
	#pprint.pprint(objList)



	put_object_with_acl(cName)

	put_object_acl(cName,objKey)



	list_multipart_uploads(cName)
	list_object_versions(cName)
	list_objects(cName)
	list_parts(cName,objKey)
	restore_object(cName,objKey)

	upload_file(cName)


	#if you want to download a file and validate its contents, use this
	dlFile = upload_file(cName)
	download_file(cName,dlFile)


	create_multipart_upload(cName)
	upload_part(cName)
	upload_part_copy(cName,objKey)
	abort_multipart_upload(cName,objKey)
	complete_multipart_upload(cName,objKey)

	copy_object(cName,objKey)

	delete_object(cName,objKey)
	delete_objects(cName,objList)


	get_slew_object_ops(cName,objKey)
	head_object(cName,objKey)






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
##bucket in the list (loadgen-bucket typicallly on topo12). don't use for 'delete_bucket'
#
bucket_list = list_buckets()
print "got bucket list"


#pprint.pprint(bucket_list)

cName = bucket_list['Buckets'][0]['Name']

#print cName

#
#if you want to use 'delete_bucket', then uncomment following
#

cName = bucket_list['Buckets'][-1]['Name']
#print cName



# for funcs in  dir(sys.modules[__name__]):
# 	myfunc = getattr(sys.modules[__name__],funcs)
# 	if callable(myfunc):
# 		#print dir(myfunc)
# 		print "%s, %s" % (myfunc,myfunc.func_code.co_argcount)

# #
#do_stuff
#

if 'all' in tests:
	tests_all(cName)
else:
	myfunc =  getattr(sys.modules[__name__],tests)
	#
	#sometimes we need to specify different args..
	#
	if myfunc.func_code.co_argcount == 1:
		#following is a hack..
		argIndex = myfunc.func_code.co_argcount - 1
		if 'cName' in myfunc.func_code.co_varnames[argIndex]:
			myfunc(cName)
		elif 'objKey' in myfunc.func_code.co_varnames[argIndex]:
			myfunc(objKey)











