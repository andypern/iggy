#S3cmd lab

**Note: in order to run this lab, you'll need to have completed the pre-requisites previously defined**

Note: much of the information contained in this lab can also be found here: https://community.igneous.io/hc/en-us/articles/223409967


##Goals

After you have completed this lab, you will have done the following items using s3cmd:

* Loaded, created a configuration file
* List all buckets
* List Keys within a bucket
* Copy files to a bucket
* Download file(s) from a bucket
* Sync a local folder to a bucket


## Configuration

By default, s3cmd will try and look for a file named `.s3cfg` in your homedirectory (`windows users`: this location may vary).  If you will be using s3cmd a lot, it makes sense for you to populate this file with the parameters required to connect to the Igneous DataService which your administrator has provided you access to.  

If you have access to the Igneous management interface (some of you may), you can follow the steps listed in the [Quick Start Guide](https://community.igneous.io/hc/en-us/articles/223443448) .  

If you do not have access to the Igneous Management interface, you will need to request the following from a lab guide, or from whomever administers your Igneous Data Service:

* endpoint URL
* access_key
* secret_key
* (optional): personalized `.s3cfg` file

Luckily, Igneous provides the ability for your administrator to send you a fully populated, personalized `.s3cfg` file which can easily be put into place on your local system.

Once you have received an `.s3cfg` file from your administrator, open it up in a text editor (windows users, use wordPad):

Inside, you should see contents similar to:

    [default]
    access_key = MJ96N3L3BA4IJ9C1YI1x
    secret_key = AxgWTyDS9ZQdPgc3Y7eJREUVF5qBFJqaAwWEY02x
    host_base = 10.105.0.21
    host_bucket =
    use_https = False

The access_key and secret_key can also be used in other applications which require those parameters (such as a python script, or an application such as CyberDuck or ARQ).  Check with your lab instructor or administrator to ensure that the host_base value is correct for the system you will be connecting to.  Assuming all is well, you can simply copy this file:

**Mac & Linux users**:

    cp /path/to/downloaded/s3cfg_file ~/.s3cfg

**Windows users**:

***NEED TO FILL THIS IN***


##Test connection & List buckets

The simplest way to test if your configuration is valid is to list all buckets.  

**Linux & Mac users**:

    s3cmd ls

**Windows users**:

    python.exe s3cmd -c %homepath%\s3cfg.cfg ls

If you see a list of buckets similar to this, then you're OK:

    2016-02-18 05:23  s3://cs-perf-testing
    2016-01-22 20:00  s3://myBucket
    2016-01-26 03:42  s3://testContainer
    2016-01-26 03:47  s3://newBucket


***Note: just because you can see a bucket in the list, does not mean you have access to it***

###List objects in a bucket

***Note: in this document as well as in others, you may see the following words used interchangeably***:
* key
* object

Basically, any 'file' or 'directory' that exists within the Igneous DataService is referenced by its 'Key'.  Also, any 'file' which gets uploaded into the Igneous DataService is known as an 'Object'.

Next, you will list objects which exist within a shared bucket on your Igneous DataService.  Simply run the following command:

**Linux & Mac users**:

    s3cmd ls s3://classbucket

**Windows users**:

    python.exe s3cmd ls s3://classbucket

If all went well, you should see something similar to:

    DIR   s3://andypern/demo_index/
    DIR   s3://andypern/logs/
    2016-08-01 14:57 209715200   s3://andypern/200mb.file
    2016-06-02 20:28       491   s3://andypern/Important.txt.new
    2016-06-02 20:29         7   s3://andypern/bla.txt.rtf.new

Note that `s3cmd` is able to identify 'directories' vs 'files'.  The output is somewhat similar to standard unix `ls` output.  Note that the column to the far right denotes the full URI that can be used for subsequent operations.

You will also want to list your own bucket, to make sure you have correct access to it:

    s3cmd ls s3://$username

***Note: $username should be replaced with the name of the bucket named after your login name.  It may differ from the username on your local machine***



## Upload files / PUT objects

1.  locate a file on your computer which you wish to upload.  ***Note: it is simplest if this file exists directly in your home directory***.  Alternatively, you can create a file using a text editor, make sure to save it directly to your home directory.

2.  Next, run the following command to upload it to your personal bucket:

    **Linux & Mac Users**:

        s3cmd put ~/myfile.txt s3://$username

    **Windows Users**:

        python.exe s3cmd put %homepath%\myfile.txt s3://$username

    *Again, substitute the $username for your bucket, and substitute 'myfile.txt' with whatever filename you want to upload*

3.  You can verify that your upload made it by listing the bucket again:

        s3cmd ls s3://$username

You can repeat file uploads for as many files as you wish.

## Download files / GET objects

Now that you have a file or two (or more) uploaded, you can practice downloading files to your laptop.  Its basically the same process as PUT/upload , but in the reverse.

1.  Create a folder in your homedirectory to download files into:

    **Linux & Mac Users**:

        mkdir ~/s3downloads
    **Windows Users**:

        mkdir %homepath%\s3downloads

2.  Determine the URI of the object you wish to download.  The simplest way is to perform a listing of your bucket:

        s3cmd ls s3://$username

    *As seen previously, this will print out a list of objects, and include the URI which you can use.  For example:*

        DIR   s3://andypern/demo_index/
        DIR   s3://andypern/logs/
        2016-08-01 14:57 209715200   s3://andypern/200mb.file
        2016-06-02 20:28       491   s3://andypern/Important.txt  <----here's the object key
        2016-06-02 20:29         7   s3://andypern/bla.txt.rtf.new  

3.  Armed with the URI of your object, run the following command to download it into your `s3downloads` folder:

    **Linux & Mac Users**:

        s3cmd get s3://$username ~/s3downloads
    **Windows Users**:
        pythonn.exe s3cmd s3://$username %homepath%\s3downloads

4.  Verify you can see the files locally by navigating to your local `s3downloads` folder.

##Sync a folder

S3cmd lets you sync a folder between your local machine, and your Igneous DataService.  This can be particularly useful when trying to backup documents in your homedirectory, make a daily copy of your source code tree, or other scenarios where you want to make sure you have a copy of an entire folder.  The command can sync in either direction, letting you quickly mirror an entire folder from your Igneous DataService down to your laptop.

Building on previous exercises, run the following command:


    s3cmd sync LOCAL_DIR s3://BUCKET[/PREFIX]
