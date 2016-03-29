#!/usr/bin/env python

import boto3

import os
import sys
from botocore.exceptions import ClientError

session = boto3.session.Session()

###############
# some variables you will want to set
#
prefix = 'http://'
slab = "archer"
suffix = ".iggy.bz"
port = ":7070"

#
# end of variables
##################


#
# I setup my environment variables (eg: in .bashrc/.zshrc) 
# such that I have a 'archer_ACCESS_KEY' etc
#

access_key =  os.environ.get(slab + "_ACCESS_KEY", None)
secret_key = os.environ.get(slab + "_SECRET_KEY", None)



#
#build the client session.  Note the signature version
# is required to be 's3' at this time. 
#

s3client = session.client('s3',
		aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
		endpoint_url=prefix + slab + suffix + port,
		config=boto3.session.Config(
			signature_version='s3',
			connect_timeout=60,
			read_timeout=60,
			s3={'addressing_style': 'path'})
		)


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
