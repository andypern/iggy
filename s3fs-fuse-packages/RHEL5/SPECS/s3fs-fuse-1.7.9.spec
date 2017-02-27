Name:           s3fs-fuse
Version:        1.79
Summary:        FUSE interface for S3
Release:        rhel5
Group: 		Applications/FS
License: 	GPLv2
BuildArch: 	x86_64

Source0: s3fs-fuse-%{version}.tar.gz



%description
FUSE interface for S3

%prep
%setup

%build
./autogen.sh
./configure --prefix=/usr --with-openssl

make



%install

make install


%clean
rm -rf %{buildroot}

%files

/usr/bin/s3fs
/usr/man/man1/s3fs.1

%post
ldconfig
