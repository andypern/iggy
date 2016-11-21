# S3fs-Fuse RPM for Igneous & RHEL5

Download:

*  [fuse-2.8.4-rhel6.x86_64.rpm](RPMS/fuse-2.8.4-rhel6.x86_64.rpm)
*  [s3fs-fuse-1.8.0-rhel6.x86_64.rpm](RPMS/s3fs-fuse-1.8.0-rhel6.x86_64.rpm)

## Installing
1.  Clean up existing fuse & s3fs-fuse packages:

        sudo yum erase -y fuse fuse-libs s3fs-fuse

2.  Install the new RPMs (in order!):

        sudo rpm -ivh fuse-2.8.4-rhel5.x86_64.rpm

    then:

        sudo rpm -ivh s3fs-fuse-1.79-rhel5.x86_64.rpm

3.  Make sure they made it:  

        sudo rpm -qa|grep fuse

    This should return:

        fuse-2.8.4-rhel6
        s3fs-fuse-1.8.0-rhel6

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
