# Mac & Linux pre-requisites

Many of the following steps apply both to Linux as well as OSX.  When there are specific differences between the commands used, you will be directed to either `Linux users`, or `Mac users`

If you are logged into a linux workstation or shared server, some of these tools may already be installed.  Depending on the specific distribution of linux that you are running, some of the commands may differ slightly from what is shown here.  The following assumes you are running RHEL7 or Centos 7.  The main dependency is python 2.7.x.  ***Note that this lab will not work with python 3+***


At bare minimum, you will need sudo or administrative privileges (to be able to install packages and software).  If you do not have this privilege level, please inform the one of the lab facilitators and they will assist you.

For s3cmd & python exercises, you will need to be familiar with how to open and use a terminal window.



## Python pre-req's


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
		simply use the password which you use to login to your Mac*


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




## s3cmd


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

## Optional : setup jupyter

Jupyter is a notebook based python environment which makes it easy to experiment and share scripts with others.  

To install:

    pip install Jupyter


To run:

1.  Change directories to a folder which has python notebooks in it, or where you wish to save some.  This can also be a top level folder.
2.  Run:

        jupyter notebook

This will stay running in your terminal's foreground, and will launch a web browser which you can then interact with.  If you wish to stop Jupyter , simply go back to the terminal in which you launched it, and press `Crtl-c`
