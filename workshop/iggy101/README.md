#Igneous 101


##Overview

The goal of this lab exercise is to get you familiar with accessing your on premises Igneous Data Service, so that you can :

* ingest data using a variety of tools
* Understand the enhanced metadata capabilities of an ObjectStore



## Pre-requisites

Note that depending on network and security conditions, you may also have access to a server which has the needed pre-requisites installed.  One of the lab facilitators will provide you with details in this case.


###Mac & Linux

Many of the following steps apply both to Linux as well as OSX.  When there are specific differences between the commands used, you will be directed to either `Linux users`, or `Mac users`

If you are logged into a linux workstation or shared server, some of these tools may already be installed.  Depending on the specific distribution of linux that you are running, some of the commands may differ slightly from what is shown here.  The following assumes you are running RHEL7 or Centos 7.  The main dependancy is python 2.7.x.


At bare minimum, you will need sudo or administrative privileges (to be able to install packages and software).  If you do not have this privilege level, please inform the one of the lab facilitators and they will assist you.

For s3cmd & python exercises, you will need to be familiar with how to open and use a terminal window.


####MISC pre-req's

Not all of these tools are necessary, but are helpful.  Many of you will already have these installed, if so, feel free to skip this section.


* homebrew
* wget
* git
* 


####Python pre-req's

Note, for s3cmd to work, you'll want to do the installation of pip/boto3 first, since the command relies on boto.

1.  Open a terminal window, and create a directory to work in during the lab

		mkdir ~/iggylab && cd ~/iggylab
	

2.  Next, validate the version of Python that you have.  The scripts you will be using today were written to work with Python 2.7.x.
	a.  Open a terminal, and run:
	
			python --version
	You should see output similar to:

			Python 2.7.11
	b.  If you see a version number that is _NOT_ 2.7.x, please notify one of the lab instructors and they will help you address the situation.

3.  `Mac users`, skip this step	.  `Linux users` you'll need to get easy_install setup to proceed.
	a.  Run:
	
			sudo yum install -y python-setuptools

4.  Install 'pip', to allow for installation of additional python modules:
	a.  Open a terminal, and run:
	
			sudo easy_install pip		
		
		*This may prompt you for a password, `Mac Users`: 
		simply use the password which you use to login to your Mac
		
		
	b.  Verify it has been installed:
	
			which pip
		
	c.  you should see output such as:
	
		/usr/local/bin/pip

5.  Get the necessary python modules installed:
	a.  First, boto3:
	
			sudo pip install --ignore-installed boto3
		
	b.  Make sure it got installed:
	
			python -m boto3
	
	c.  You should see output such as:
	
			/usr/local/opt/python/bin/python2.7: No module named boto3.__main__; 'boto3' is a package and cannot be directly executed

	If you only see `No module named boto3` , it means it was unable to install.  Please notify one of the lab facilitators.
	
	
	

####s3cmd


There is a simple walkthrough of s3cmd located here:  https://igneoussystemshelp.zendesk.com/knowledge/articles/223409967/en-us?brand_id=1018328

Here is a condensed set of steps to get it installed quickly:

1.  make sure you are in your iggylab folder:

		cd ~/iggylab 
2. Download the s3cmd tarball:

		curl -L -O http://downloads.sourceforge.net/project/s3tools/s3cmd/1.6.1/s3cmd-1.6.1.tar.gz
3.  Unpack it and navigate to the folder created:

		tar -xzf s3cmd-*.tar.gz  && cd s3cmd-*
4.  Run the installer:

		sudo python setup.py install
		
	The final line of output should look like so:
	
	`Finished processing dependencies for s3cmd==1.6.1`
	
5.  Assuming you got no errors, run the following to verify that its in place:

		 which s3cmd
	 Output should be similar to:
	 
	`/usr/local/bin/s3cmd`
	
S3cmd is now installed!







###Windows






