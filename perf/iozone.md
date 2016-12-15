get and install:

	wget http://www.iozone.org/src/current/iozone-3-465.i386.rpm
	yum install -y iozone-3-465.i386.rpm

fix /etc/profile:

	PATH=/opt/iozone/bin:$PATH
	source /etc/profile



run:

	iozone -s 10000000 -r 1024 -f /mnt/s3/iozone/temp

	
