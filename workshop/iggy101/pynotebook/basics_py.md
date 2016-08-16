

# Python lab


## Other reading

You may also find information on using the boto3 python library here:

* [Using Boto3 - AWS's SDK for Python](https://igneoussystemshelp.zendesk.com/knowledge/articles/222814587)

* [Boto3 - Retry operations](https://igneoussystemshelp.zendesk.com/knowledge/articles/223204708)


## Import modules
To begin with, execute the following code to import the modules needed for this exercise:

```python
import boto3
import tempfile

import botocore.utils as boto_utils

print "imported modules"

```



## Instantiate variables
You'll need to input a few things in order to get started.  
'bucket': This is your target bucket, similar to a filesystem directory without the hierarchy. In the Igneous User Interface, buckets are referred to as containers.   

**'access_key'**: The access key which identifies who you are to the server.  You can obtain this from your IT administrator.  This is similar to a ‘username’.

**'secret_key'**: A secret key which authenticates you to the server.  You would also obtain this from your IT administrator.  This is similar to a ‘password’.  As such, you should refrain from storing the secret_key directly in your scripts, especially if they are to be placed in a shared location.  

**'endpoint_url'**: This is the URL which hosts your Igneous Data Service.  If you are unsure what to put here, please consult with your IT Administrator.  Typically the endpoint URL would look something like this:  http://igneous.company.com:80 , or https://igneous.company.com:443.

**Note: if you specify a URL which contains ‘https’ , you will need to change the ‘use_ssl’ parameter to ‘True’.**




```python
access_key=''
secret_key=''
endpoint_url='http://sd-igneous.qualcomm.com:7070'
use_ssl = False

print "variables set"

```

## Setup connection parameters

You don't need to change anything here, but take notice of what we're doing. Baiscally, we're taking the access_key and secret-key , and creating a session object which we will later use to establish a connection.


```python

def boto3_session(access_key, secret_key):

    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)

print "session function created"

```

Once we h ave the session object, Here's how to create a connection constructor.  Note that we're calling the 'boto3_session' function from within the boto3_s3_client function.

```python
def boto3_s3_client(access_key, secret_key, endpoint_url):

    # Create a session and then a client from it.
    session = boto3_session(access_key, secret_key)
    client = session.client(
        's3',
        region_name='iggy-1',
        use_ssl=False,
        verify=False,
        endpoint_url=endpoint_url,
        config=boto3.session.Config(
            signature_version='s3',
            s3={
                'addressing_style': 'path'
            }
        ))

    # All finished here. We can start using the client as expected now
    return client

print "client function created"
```

Now you can actually call it..note that it won't 'do' anything yet.  But we'll print out the object so you can verify that it returned.

```python

client = boto3_s3_client(access_key, secret_key, endpoint_url)
print client

```



## Test connnection & List buckets
Note that merely creating and executing a connection constructor isn't enough to know if its working, you actually have to *use* it.  Therefore, to test it out, lets have it list buckets


```python
def list_buckets(client):

    # See the following URL for more details about this call:
    # http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_buckets
    lsb_resp = client.list_buckets()

    for bucket in lsb_resp['Buckets']:
        yield bucket['Name']
```

Now call it, and see what prints out:

```python

bucket_list = list_buckets(client)

for bucket in bucket_list:
    print bucket

```


## List objects

Now that you know how to get a list of buckets, you can write a function to list the objects within one (or more) of them, provided your access/secret key has access.

First, lets define the function:


```python


def list_objects(client, bucket):
    """
    Return a generator that iterates through the keys contained within the
    specified bucket.
    """

    # See the following URL for more details about this call:
    # http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_objects
    lsb_resp = client.list_objects(
        Bucket=bucket)

    for obj in lsb_resp['Contents']:
        yield obj['Key']

print "list_objects function created"
```


Now, call it.  You will first have to define the bucket you want to list though.  Keep in mind that you probably don't want to choose a bucket that has a lot of objects in it, since the printout will take time and screen real estate.

```python

bucket='mybucket'
objList = list_objects(client, bucket)

for objKey in objList:
    print objKey

```


## Put an object

In order to put an object, you some content.  This can either be a file (more specifically, the contents of a file), or it can simply be some data (we'll use text data)

First you'll set a variable to hold some text, and we'll shove it into a tempfile.

```python

TEST_TEXT = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do '
             'eiusmod tempor incididunt ut labore et dolore magna aliqua.')

fd = tempfile.TemporaryFile()
fd.write(TEST_TEXT)
fd.flush()
fd.seek(0)

print fd.read()
```

Next, lets define a function which will do the actual work of uploading:


```python
def put_object(client, bucket, key, fd):

    # See the following URL for more details about this call:
    # http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.put_object
    put_resp = client.put_object(
        Body=fd,
        Bucket=bucket,
        Key=key
    )

    # Return the object's version
    return put_resp

print "put_object function defined"
```

In order to run it, we'll call it and pass it some variables & objects that we got from before:

```python
objKey = "tempfile"
put_object(client,bucket,objKey,fd)
fd.close()

```

## Get object

So you uploaded an object, congrats!  next, lets define a function that will perform a 'get' on that object, and print the contents out to the screen.  

```python
def get_object(client, bucket, key):

    # See the following URL for more details about this call:
    # http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_object
    get_resp = client.get_object(
        Bucket=bucket,
        Key=key)

    return get_resp['Body']
```

Now call it, specifying the key name.  

```python

objKey = "mykey"
objContents = get_object(client, bucket, objKey)
print objContents


```


## Head object

The `head_object` method allows you to get metadata, including extended metadata on an individual object basis.

First, define the function:

```python
def head_object(client, bucket,objKey):
	try:
		response = client.head_object(
			Bucket=bucket,
			Key=objKey)
        return response

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		#print error_code
		return "failed: %s" %(error_code)

print "defined head_object function"
```

Next, lets actually run it:

```python

objKey = "mykey"
objMeta = head_object(client, bucket, objKey)
print objMeta




## Delete object

now its time to cleanup after yourself, basically you want to delete the object you just created.

First, define the function:

```python
def delete_object(client, bucket, key):

    # See the following URL for more details about this call:
    # http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.delete_object
    get_resp = client.delete_object(
        Bucket=bucket,
        Key=key)

    return get_resp
```


Now, actually call it

```python

delete_response = delete_object(client, bucket, objKey)
print delete_response
```

## string it all together

well, what if you want to run all of this, at once?

First, define a function that does all of the things we want:



```python
def run_example(bucket, access_key, secret_key, endpoint_url):

    # Create a new client to play with
    client = boto3_s3_client(access_key, secret_key, endpoint_url)

    # List the buckets to see what's in the root context
    print('Listing buckets...')
    for b in list_buckets(client):
        print(b)

    # Let's generate something to put into a bucket
    fd = tempfile.TemporaryFile()
    fd.write(TEST_TEXT)

    # Make sure the file is flushed and then seek to the start for reading
    fd.flush()
    fd.seek(0)

    # Put the object - passing a file object here is okay
    version_1 = put_object(client, bucket, 'test', fd)

    # Clean up the temp file
    fd.close()

    # Put the object again - passing a string or bytearray also works for this call
    version_2 = put_object(client, bucket, 'test', TEST_TEXT)

    print('Version started at: {}. Latest object version: {}.'.format(
        version_1, version_2))

    # Get the object
    object_fd = get_object(client, bucket, 'test')
    object_content = object_fd.read()

    print('Body of object: "{}"'.format(
        object_content))

    print('Put content matches retrieved content: {}'.format(
        object_content == TEST_TEXT))

    # List the objects in the bucket now
    print('Listing objects...')
    for key in list_objects(client, bucket):
        print(key)

    # Delete the object we put
    del_version = delete_object(client, bucket, 'test')

    print('Deleted object. Version is now: {}'.format(del_version))

```
Now...run it.


```python
# Run the example!
if __name__ == '__main__':
    run_example(
        bucket='',
        access_key='',
        secret_key='',
        endpoint_url='')
```
