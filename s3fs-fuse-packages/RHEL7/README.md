# S3fs-Fuse RPM for Igneous & RHEL7

Download:

*  [s3fs-fuse-1.8.0-rhel7.x86_64.rpm](RPMS/s3fs-fuse-1.8.0-rhel7.x86_64.rpm)

Place the file on the machine you wish to install on.

## Installing
1.  Install fuse RPM:

        sudo yum install -y fuse

2.  Install the s3fs-fuse RPM:

	 sudo yum install -y s3fs-fuse-1.8.0-rhel7.x86_64.rpm

3.  Make sure  made it:  

        sudo rpm -qa|grep s3fs-fuse

    This should return:

        s3fs-fuse-1.8.0-rhel7

4.  Enable fuse module:

        sudo modprobe fuse

4. Verify that s3fs is executable:

        which s3fs
    Also:

        s3fs -h

    Should return:

        s3fs: missing BUCKET argument
        Usage: s3fs BUCKET:[PATH] MOUNTPOINT [OPTION]...


## Using

1.  Make a ~/.passwd-s3fs file w/ following contents:

        accessKeyId:secretAccessKey

    ***obviously, replace with the appropriate access_key & secret_key***

2.  Make password file r/o:

        chmod 600 ~/.passwd-s3fs

3.  Make a folder where you can mount your bucket to (substitute `mybucket` with the name of the container/bucket you want to mount):

        mkdir /mnt/myBucket

4.  Finally, run the following

```
    s3fs myBucket /mnt/myBucket \
    -o url=http://endpoint_ip:7070 \
      -o use_path_request_style \
      -o passwd_file=~/.passwd-s3fs \
      -o sigv2 \
      -o allow_other
```
***substitute the appropriate hostname/IP for `endpoint_ip`***
