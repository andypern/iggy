#!/usr/bin/env python

from dateutil import parser

import pprint
import datetime
import time
import os
import sys
import ConfigParser
import argparse
import re

import json
import elasticsearch
from elasticsearch import Elasticsearch
import base64







#TODO:




					#print index_result
					#self.queue.task_done()


class Ddict(dict):
    def __init__(self, default=None):
        self.default = default

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)









def objIndexer(fileName,es_cluster,es_index,es_type,encodedString):

	es = Elasticsearch(
	[es_cluster],
	port=9200
	)

	body_hash = {}

	index_id = fileName
	body_hash['file'] = encodedString

	for attempt in range(5):
		try:

			res = es.index(index=es_index, doc_type=es_type, id=index_id, body=body_hash)
			break
		except TypeError as e:
			print "issue inserting: %s -> %s (typeerr)" %(index_id,e)
			break
		except AttributeError as e:
			print "issue inserting: %s -> %s (attr_error)" %(index_id,e)
			break
		except elasticsearch.exceptions.ConnectionError as e:
			print "%s / %s : insertion error: %s , try # %s" %(fileName,e,attempt)
			backoff = (2 ** attempt)
			time.sleep(backoff)
			continue

	return res






def getArgs():

	argparser = argparse.ArgumentParser(description = "index docs")






	argparser.add_argument('-c', '--cluster',
	help = "elastic search cluster, eg: my.hostname.com",
	dest='es_cluster',
	required=True)

	argparser.add_argument('-f', '--file',
	help = "path to file",
	dest='fileName',
	required=True)



	argparser.add_argument("-i", "--index", dest="es_index", default="demo")
	argparser.add_argument("-t", "--type", dest="es_type", default="fsindex")


	args =  argparser.parse_args()



	return args.fileName,args.es_cluster,args.es_index,args.es_type





#########
#end of functions
#########


if __name__ == "__main__":
	#delete these
	result_hash = Ddict( dict )

	# get args
	fileName,es_cluster,es_index,es_type = getArgs()

	try:
		fh = open(fileName,'r')
	except:
		print "couldn't open %s" %(fileName)
		sys.exit(1)
	encodedString = base64.b64encode(fh.read())



	index_result = objIndexer(fileName,es_cluster,es_index,es_type,encodedString)
