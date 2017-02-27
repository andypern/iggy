https://github.com/libfuse/libfuse/releases/download/fuse_2_9_4/fuse-2.8.4.tar.gz

https://github.com/libfuse/libfuse

./configure
make -j8
make install

ln -s /usr/local/lib/pkgconfig/fuse.pc /usr/lib/pkgconfig/fuse.pc
export PKG_CONFIG_PATH=/usr/lib/pkgconfig

ln -s /usr/local/lib/libfuse.so.2 /lib64/libfuse.so.2

# Centos 5 & 6


Esp for VM's, make sure the time is all good:

```yum install -y ntp
ntpdate -b bigben.cac.washington.edu
```
## install fuse

yum install -y automake
yum install -y gcc libstdc++-devel gcc-c++ curl-devel libxml2-devel openssl-devel mailcap

yum erase -y fuse fuse-devel





export CC=/usr/bin/gcc
export CPP=/usr/bin/cpp
export CXX=/usr/bin/g++



tar -xzf fuse-2.8.4.tar.gz
cd fuse-2.8.4

./configure --prefix=/usr

make -j8


make install

export PKG_CONFIG_PATH=/usr/lib/pkgconfig

verify w/ :

pkg-config --modversion fuse



### make RPM for fuse
yum install -y rpm-build


#### Centos 5 only
Note: different spec file for RHEL5

 ```
 cp fuse-2.8.4.tar.gz /usr/src/redhat/SOURCES/

 put SPEC file into /usr/src/redhat/SPECS/

 rpmbuild -bb /usr/src/redhat/SPECS/fuse_284.spec
```

#### Centos 6 only
Note: different spec file for RHEL6
```
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

 cp fuse-2.8.4.tar.gz /root/rpmbuild/SOURCES/
 cp fuse_284.spec /root/rpmbuild/SPECS/
 rpmbuild -bb /root/rpmbuild/SPECS/fuse_284.spec
 ```




## install s3fs-fuse
Esp for VM's, make sure the time is all good:

```
yum install -y ntp
ntpdate -b bigben.cac.washington.edu
```
first make sure that you have fuse-2.8.4 installed either manually or via built RPM.

### pre-req's
(you might already have these, but it doesn't hurt)
yum install -y automake
yum install -y gcc libstdc++-devel gcc-c++ curl-devel libxml2-devel openssl-devel mailcap


### install git (centos5 only)

yum install -y wget
wget --no-check-certificate https://www.kernel.org/pub/software/scm/git/git-2.0.1.tar.gz

tar -xzf git-2.0.1.tar.gz
cd git-2.0.1
./configure
make
make install

### Install git (centos 6)
yum install -y git


### grab s3fs-fuse source & checkout

cd /root
git clone https://github.com/s3fs-fuse/s3fs-fuse
cd s3fs-fuse/
`Centos 5 only`:
	git checkout cbc057bca718726e1307aa024004389fcf17fee0

`All rev's`:

./autogen.sh

./configure --prefix=/usr --with-openssl
make
make install


### build RPM for s3fs-fuse
yum install -y rpm-build


cd /root/s3fs-fuse
make clean
cd ..

#### Centos 5

mv s3fs-fuse s3fs-fuse-1.79

tar -czf s3fs-fuse-1.79.tar.gz s3fs-fuse-1.79


cp s3fs-fuse-1.79.tar.gz /usr/src/redhat/SOURCES/

copy spec file to /usr/src/redhat/SPECS/s3fs-fuse-1.7.9.spec

rpmbuild -bb /usr/src/redhat/SPECS/s3fs-fuse-1.7.9.spec


#### Centos 6

mv s3fs-fuse s3fs-fuse-1.8.0

tar -czf s3fs-fuse-1.8.0.tar.gz s3fs-fuse-1.8.0



Note: different spec file for RHEL6
```
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

 cp s3fs-fuse-1.8.0.tar.gz /root/rpmbuild/SOURCES/
 cp s3fs-fuse-1.8.0.spec /root/rpmbuild/SPECS/
 rpmbuild -bb /root/rpmbuild/SPECS/s3fs-fuse-1.8.0.spec
 ```


# Centos 7

This should be easier..

## pre-req's

sudo yum install automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel

Note that its installing fuse-2.9 by default on cent7, no need for a fuse RPM.

## s3fs-fuse

git clone https://github.com/s3fs-fuse/s3fs-fuse.git
cd s3fs-fuse
./autogen.sh
./configure
make
sudo make install

## building an RPM for s3fs-fuse

yum install -y rpm-build
cd /root/s3fs-fuse
make clean
cd ..

mv s3fs-fuse s3fs-fuse-1.8.0

tar -czf s3fs-fuse-1.8.0.tar.gz s3fs-fuse-1.8.0


Note: different spec file for RHEL6
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

cp s3fs-fuse-1.8.0.tar.gz /root/rpmbuild/SOURCES/
cp s3fs-fuse-1.8.0.spec /root/rpmbuild/SPECS/
rpmbuild -bb /root/rpmbuild/SPECS/s3fs-fuse-1.8.0.spec





# OSX
	brew install automake
	brew install Caskroom/cask/osxfuse




# appendix


## not needed (install new gcc)
http://superuser.com/questions/381160/how-to-install-gcc-4-7-x-4-8-x-on-centos



cd /etc/yum.repos.d
wget http://people.centos.org/tru/devtools-1.1/devtools-1.1.repo

yum --enablerepo=testing-1.1-devtools-5 install devtoolset-1.1-gcc devtoolset-1.1-gcc-c++
