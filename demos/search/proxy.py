#!/usr/bin/python
# This script starts a proxy which can relay to an iggy box.  The goal is to intercept
# PUT requests , extract metadata, and populate an ES index.  This is for demo purposes only, and
# will have LOTS of race conditions, data inconsistencies, etc.
#
#original proxy code borrowed from voorloop_at_gmail.com

######TODO
# * figure out crtl-c to kill all threads
# * detect 'ifdir' or something (no need: content-type works)
# * typing before insertion? (content-length = int?)<-necessary?

import argparse
import socket
import select
import time
import sys
import httplib
import os
from datetime import datetime
from elasticsearch import Elasticsearch

from multiprocessing import Process, JoinableQueue, Queue

#
#variables
#
threadcount = 5

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things

buffer_size = 4096
delay = 0.0001
#
#http request parsing class, taken from http://goo.gl/Q96AKg 
#
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


#
# also need to parse responses, from http://goo.gl/opYG4P
#

from httplib import HTTPResponse

#
#we sort of have to trick things here by creating a fake socket to pass our string into
# 

class FakeSocket():
    def __init__(self, response_str):
        self._file = StringIO(response_str)
    def makefile(self, *args, **kwargs):
        return self._file


#
#build a dict class to get some anonymous hash going on
#

class Ddict(dict):
    def __init__(self, default=None):
        self.default = default

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)

def getArgs():

    parser = argparse.ArgumentParser()

    script = os.path.basename(sys.argv[0])
    usage = 'Usage: ' + script + '-l listen_port -e endpoint -c es_cluster -i index -t es_type -n numThreads -v verbose'

    parser.add_argument("-l", "--listen", dest="listen_port", default=9090)
    parser.add_argument("-e", "--endpoint", dest="endpoint", required=True)
    parser.add_argument("-c", "--cluster", dest="es_cluster", required=True)
    parser.add_argument("-i", "--index", dest="index_name", default="demo")
    parser.add_argument("-t", "--type", dest="es_type", default="fsindex")
    parser.add_argument("-n", "--num-threads", type=int, dest="num_threads", default=5)
    parser.add_argument("-v", "--verbose", dest="verbosity", default=False)


    args = parser.parse_args()
    
    if (args.endpoint is None): 
        parser.print_help()
        sys.exit(1)
    else: 
        forward_to = args.endpoint.split(":")

    return args.listen_port,forward_to, args.es_cluster, args.index_name, args.es_type, args.num_threads



class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port, forward_to):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)
        self.forward_to = forward_to

        print self.forward_to

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(self.forward_to[0], int(self.forward_to[1]))
        clientsock, clientaddr = self.server.accept()
        if forward:
            #print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock

        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_close(self):
        #print self.s.getpeername(), "has disconnected"
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        #we don't want to block pushing the request/response , so send it first
        self.channel[self.s].send(data)


    
        

        #once its sent on its way, lets parse it
        #for now, we'll parse in main thread, but perhaps it makes sense 
        #to parse from a separate queue.

        parse_result = header_handler(data)
        if len(parse_result) > 0:

            file_queue.put(parse_result)
            #index_result = indexer(parse_result)


class indexer(Process):

    def __init__(self,file_queue,result_queue,es_cluster,index_name,es_type):
        Process.__init__(self)
        self.file_queue = file_queue
        self.result_queue = result_queue
        self.es_cluster = es_cluster
        self.index_name = index_name
        self.es_type = es_type
        


    def run(self):
        proc_name = self.name
        #
        #there are some situations where we will want to throw away the header, specifically when
        # we think that the metadata wasn't actually saved.  We know when these can happen (x-amz-metadata-directive=REPLACE)
        # however for now we'll just use everything we see.
        #

        

        es = Elasticsearch(
            [self.es_cluster],
            port=9200
        )


        while True:
            phat_hash = self.file_queue.get()
            #makes sense for ID to be the objectKey
            index_id = phat_hash['path']
            
            #print phat_hash

            index_id = phat_hash['path']
            res = es.index(index=self.index_name, doc_type=self.es_type, id=index_id, body=phat_hash)
            print res

            self.result_queue.put(res)
        
        print(res)
        
      


        


def header_handler(http_data):
            #parse the request/response
        http_request = HTTPRequest(http_data)

        phat_hash = Ddict( dict )
        #We only care about requests for our purposes
        # in reality, we should only care about requests that get responded to positively
        # that  might be hard to do though.

        # if there's no command..its a response (not a request)
        if http_request.command != None:
            #
            #we only care about PUT's
            #
            if http_request.command in "PUT":
                phat_hash['command'] = 'PUT'
                phat_hash['path'] = http_request.path
                for key in http_request.headers.keys():
                    #strip things we don't care about
                    if 'connection' in key:
                        #do nothing..
                        pass
                    elif 'authorization' in key:
                        pass
                    elif 'expect' in key:
                        pass
                    else:
                        phat_hash[key] = http_request.headers[key]
 
        # else:
        #     #commenting most out for now, we don't really care about responses
        #     #phat_hash['header_type'] = "response"
        #     #this is a response
        #     socket_string = FakeSocket(http_data)
        #     http_response = HTTPResponse(socket_string)
        #     try:
        #         http_response.begin()
        #         #
        #         #if the response is just an HTTP continuation ack, ignore it
        #         #
        #         if len(http_response.getheaders()) > 0:
        #             #print http_response.getheaders()
        #             isResponse = True
        #     except httplib.BadStatusLine as e:
        #         isHeader = False
        #         #print "this isn't a header, skippping"

        return phat_hash


if __name__ == '__main__':

    listen_port,forward_to, es_cluster, index_name, es_type, num_threads = getArgs()

    server = TheServer('', listen_port, forward_to)
    #
    #launch processes for doing work
    #
    file_queue = JoinableQueue()
    result_queue = Queue()
    file_processes = [ indexer(file_queue, result_queue,es_cluster,index_name,es_type)
                      for i in range(num_threads) ]    




    #
    #actually kick off daemons
    #

    for w in file_processes:
        w.start()

    #
    #now just get the proxy started
    # 

    try:
        server.main_loop()
    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)
