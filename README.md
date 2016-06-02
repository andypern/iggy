#Boto3 basics

This folder contains a number of basic scripts intended to illustrate how to use the boto3 python library to interact with an Igneous system.

##Pre-req's


* Python 2.7.11 , although they should probably work with any revision >=2.6, as boto3 is tested against a wide variety of modern versions.
* Boto3 library ( https://github.com/boto/boto3 ).  Simplest install is via 'pip install boto3'. If you need pip, try google.


##Scripts

* s3_boto3_connect.py : shows how to build a connection by supplying CLI arguments for host, key, secret, etc.  Upon successful connection, it will print out a list of containers (buckets) and exit.
