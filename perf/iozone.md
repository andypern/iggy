get and install:

	wget http://www.iozone.org/src/current/iozone-3-465.i386.rpm
	yum install -y iozone-3-465.i386.rpm

fix /etc/profile:

	PATH=/opt/iozone/bin:$PATH
	source /etc/profile



run:

	iozone -s 1g -r 1m -f /mnt/bstor/iozone/temp

writes:

	iozone -C -s 1g -r 1m -i 0 -w -f /mnt/bstor/iozone/temp

Direct:
	iozone -C -s 1g -r 1m -I -i 0 -w -f /mnt/bstor/iozone/temp


reads:

	iozone -C -s 1g -r 1m -i 1 -f /mnt/bstor/iozone/temp



	/opt/iozone/bin/iozone -C -s 4g -r 1m -i 0 -w -t 1 -F /mnt/goofy/goofy/temp1
