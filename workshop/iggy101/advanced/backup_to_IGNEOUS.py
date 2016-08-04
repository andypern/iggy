from boto3.s3.transfer import S3Transfer
from boto3.s3.transfer import TransferConfig

import boto3
import threading
import os
import sys

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


client = boto3.client (
	's3',
	use_ssl=False,
	endpoint_url='http://igneousdemo.iggy.bz/',
	aws_access_key_id='IGNEOUSACCESSKEY',
	aws_secret_access_key='IGNEOUSSECRETKEY'
)

config = TransferConfig(
	multipart_threshold= 8 * 1024 * 1024 * 1024,  # Set threshold to 8GB before using Multipart
	max_concurrency=10,
)

transfer = S3Transfer(client, config)

rootDir = '/mnt/data'

for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
	#transfer.upload_file(dirName, 's3container', dirName,
	#		extra_args={'Metadata': {'upload-date': '2016-05-14 21:45:00 PST', 'os': 'linux'}},
	#		callback=ProgressPercentage(dirName))
	for fname in fileList:
		try:
			filename = '{0}/{1}'.format(dirName,fname)
			#print('\tuploading file {0}\n'.format(filename))
			transfer.upload_file(filename, 's3container', filename,
				extra_args={'Metadata': {'upload-date': '2016-05-14 21:45:00 PST', 'os': 'linux'}},
				callback=ProgressPercentage(filename))
		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)




print "Success"
