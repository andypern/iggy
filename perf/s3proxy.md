quick download: https://github.com/andrewgaul/s3proxy/releases/download/s3proxy-1.5.1/s3proxy

sudo apt-get install openjdk-7-jre

chmod +x s3proxy

make a config file that looks like this:

```
s3proxy.authorization=none
s3proxy.endpoint=http://127.0.0.1:8080
jclouds.provider=filesystem
jclouds.filesystem.basedir=/bigdrive
```

in a screen session:

	sudo ./s3proxy --properties s3proxy.conf


Use this for s3cmd:

```
[default]
access_key = local-identity
secret_key = local-credential
host_base = localhost:8080
host_bucket = localhost:8080
use_https = False
```
