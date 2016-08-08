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

`Mac & Linux users`:

    cp /path/to/downloaded/s3cfg_file ~/.s3cfg

`Windows users`:

***NEED TO FILL THIS IN***


##Test connection & List buckets

The simplest way to test if your configuration is valid is to list all buckets.  

`Linux & Mac users`:

    s3cmd ls

`Windows users`:

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

`Linux & Mac users`:

    s3cmd ls s3://classbucket

`Windows users`:

    python.exe s3cmd ls s3://classbucket