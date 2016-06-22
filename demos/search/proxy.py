#!/usr/bin/python
# This script starts a proxy which can relay to an iggy box.  The goal is to intercept
# PUT requests , extract metadata, and populate an ES index.  This is for demo purposes only, and
# will have LOTS of race conditions, data inconsistencies, etc.
#
#original proxy code borrowed from voorloop_at_gmail.com

######TODO
# * multi-threading...
# * add CLI arg's
# * detect 'ifdir' or something
# * strip fields we don't care about
# * typing before insertion? (content-length = int?)


import socket
import select
import time
import sys
import httplib
import os
from datetime import datetime
from elasticsearch import Elasticsearch

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



# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001
forward_to = ('demo.iggy.bz', 7070)

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

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

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
        forward = Forward().start(forward_to[0], forward_to[1])
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
        parse_result = header_handler(data)
        if len(parse_result) > 0:
            #print parse_result
            index_result = indexer(parse_result)



        


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
                    phat_hash[key] = http_request.headers[key]
 
        else:
            #commenting most out for now, we don't really care about responses
            #phat_hash['header_type'] = "response"
            #this is a response
            socket_string = FakeSocket(http_data)
            http_response = HTTPResponse(socket_string)
            try:
                http_response.begin()
                #
                #if the response is just an HTTP continuation ack, ignore it
                #
                if len(http_response.getheaders()) > 0:
                    #print http_response.getheaders()
                    isResponse = True
            except httplib.BadStatusLine as e:
                isHeader = False
                #print "this isn't a header, skippping"

        return phat_hash

def indexer(phat_hash):

    #print phat_hash


    #
    #there are some situations where we will want to throw away the header, specifically when
    # we think that the metadata wasn't actually saved.  We know when these can happen (x-amz-metadata-directive=REPLACE)
    # however for now we'll just use everything we see.
    #

    #
    #first we'll do a quick hack without any error checking 
    #
   
    index_id = phat_hash['path']
    INDEX = 'demo'
    TYPE = 'fstest'

   
    es = Elasticsearch(
        ['192.168.2.147'],
        port=9200
    )

    res = es.index(index=INDEX, doc_type=TYPE, id=index_id, body=phat_hash)
    print(res)

if __name__ == '__main__':
        server = TheServer('', 9090)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
            sys.exit(1)
