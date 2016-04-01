#!/usr/bin/env python

import boto3
import botocore

import xml.etree



import sys
import getopt
from string import ascii_uppercase
from random import choice







###############
# some variables you will want to set. If not, you need to specify arg's
# see next section
#
prefix = 'http://'


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






def make_session():

	session = boto3.session.Session()

	response = s3client = session.client('s3',
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
	#print_simple(response)


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
#puts
#

def put_object_basic(cName):
	#
	#basic object put, nothing special
	#
	print "+++put_object_basic+++"
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



def put_object_acl(objKey,cName):
	#
	#slightly different, we need to do this against an existing object
	#
	print "+++put_object_acl+++"

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


def create_multipart_upload(cName):
	print '+++create_multipart_upload+++'
	objKey = "multipart-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.create_multipart_upload(
	    Bucket=cName,
	    Key=objKey,
	)
		print response
	except botocore.exceptions.ClientError as e:
		print e.response


def upload_part(cName):
	print '+++upload_part+++'
	objKey = "multipart-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.upload_part(
		    Body=b'randombytes',
		    Bucket=cName,
		    Key='fake_file',
		    PartNumber=2,
		    UploadId='1234',
		)
		print response
	except botocore.exceptions.ClientError as e:
		print e.response




def upload_part_copy(cName,objKey):
	print '+++upload_part_copy+++'
	newKey = "multipart-copy-" + (''.join(choice(ascii_uppercase) for i in range(6)))

	try:
		response = s3client.upload_part_copy(
	        Bucket=cName,
		    CopySource={'Bucket': cName, 'Key': objKey, 'VersionId': '1'},
		    Key=newKey,
		    PartNumber=1,
		    UploadId='12345'
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response
	except xml.etree.cElementTree.ParseError as e:
		print "we got a 200 , but had an error that we couldn't resolve : %s" %(e)




def abort_multipart_upload(cName,objKey):
	print '+++abort_multipart_upload+++'

	try:
		response = s3client.abort_multipart_upload(
		    Bucket=cName,
		    Key=objKey,
		    UploadId='1234',
		    RequestPayer='requester'
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response



def complete_multipart_upload(cName,objKey):
	print '+++complete_multipart_upload+++'

	try:
		response = s3client.complete_multipart_upload(
		    Bucket=cName,
		    Key=objKey,
		    UploadId='1234'
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response

def copy_object(cName,objKey):
	print '+++copy_object+++'
	newKey = "copy-object-" + (''.join(choice(ascii_uppercase) for i in range(6)))


	try:
		response = s3client.copy_object(
		    Bucket=cName,
		    CopySource={'Bucket': cName, 'Key': objKey, 'VersionId': '1'},
		    Key=newKey
		)

		print response
	except botocore.exceptions.ClientError as e:
		print e.response
	except xml.etree.cElementTree.ParseError as e:
		print "we got a 200 , but had an error that we couldn't resolve : %s" %(e)







#########
#end of functions
#########

s3client = make_session()
bucket_list = list_buckets()
cName = bucket_list['Buckets'][-1]['Name']
print cName
put_bucket_lifecycle_configuration(cName)
objKey = put_object_basic(cName)
put_object_acl(objKey,cName)
upload_part(cName)
upload_part_copy(cName,objKey)
abort_multipart_upload(cName,objKey)
complete_multipart_upload(cName,objKey)
copy_object(cName,objKey)
