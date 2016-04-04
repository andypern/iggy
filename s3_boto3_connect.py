#!/usr/bin/env python

import boto3

import os
import sys
import getopt
from botocore.exceptions import ClientError

session = boto3.session.Session()

###############
# some variables need to be set. 
#
prefix = 'http://'

#
# end of variables
##################


print_verbose = False

#
#provide some CLI options.  
#

try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:a:s:v", ["host=","port=","access_key=",
        	"secret_key","verbose"])
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
	if opt in ('-v', '--verbose'):
		print_verbose = True




if len(opts) < 4:
	print "syntax is `./s3_boto3_shortlist.py -h <hostname> -p 80 -a <access_key> -s <secret_key>`"
	sys.exit(1)


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


try:
	response = s3client.list_buckets()
except ClientError as e:
	print e.message
	sys.exit(0)


#
# just dump the dictionary of buckets from the response.
# you'll probably want to do something a little more elegant.
#
print response['Buckets']
