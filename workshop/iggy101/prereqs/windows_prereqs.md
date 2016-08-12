# Windows pre-requisites


Note that this document was written and tested with Windows7 , but should work with Windows10 also.  


## Getting Python installed

1.  Grab the anaconda installer for python 2.7: http://repo.continuum.io/archive/Anaconda2-4.1.1-Windows-x86_64.exe
2.  Take all defaults.  Make sure on the 'Advanced Installation Options' page you leave both boxes Checked as shown below:

	![image](../pics/win_anaconda_install_opts.png)

	*Note: this may take several minutes to install*

3.  Once its installed, you should see an 'Anaconda2' folder in your Start menu under 'All Programs':

	![image](../pics/windows_anaconda_startmenu.png)

4.  To verify all is well, click on the 'Anaconda Prompt' icon, which should launch a command window.  Type the following into it:

	python --version

You should see something similar to:

	Python 2.7.12 :: Anaconda 4.1.1 (64-bit)

## Getting python modules & dependancies


There are a few ways to get python modules installed in Windows, the simplest is to use 'pip'.  Luckily, pip is included with the Anaconda install on windows.

1.  Go to your Anaconda Prompt window. (`All Programs -> Anaconda2 -> Anaconda Prompt`)
2.  Once there, type:
		pip install boto3

	The last line of output should look similar to this:

		Successfully installed boto3-1.4.0 botocore-1.4.43 jmespath-0.9.0 s3transfer-0.1.1


3.  For a final check, go ahead and launch `All Programs -> Anaconda2 -> Ipython` , which should give you a window which looks like this:

	![image](../pics/win_ipython_blank.png)

4.  In that window, type the following and hit the `<enter>` key:

		import boto3
	If all is well, you will not get any output to the screen.  This means that the boto3 library was successfully installed and is able to be loaded into the Python environment.


You have now got python and dependancies setup and installed on Windows!
