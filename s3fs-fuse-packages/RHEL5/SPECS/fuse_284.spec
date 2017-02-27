Name:           fuse
Version:        2.8.4
Summary:        Filesystem in Userspace
Release:        rhel5
Group: 		Applications/FS
License: 	GPLv2
BuildArch: 	x86_64

Source0: fuse-%{version}.tar.gz



%description
Filesystem in Userspace

%prep
%setup

%build
./configure --prefix=/usr

make -j8



%install

make install


%clean
rm -rf %{buildroot}

%files


/usr/include/fuse
/usr/include/fuse/fuse_common_compat.h
/usr/include/fuse/fuse_lowlevel_compat.h
/usr/include/fuse/fuse_lowlevel.h
/usr/include/fuse/cuse_lowlevel.h
/usr/include/fuse/fuse_common.h
/usr/include/fuse/fuse_compat.h
/usr/include/fuse/fuse.h
/usr/include/fuse/fuse_opt.h

/usr/include/ulockmgr.h

/usr/lib/libulockmgr.la
/usr/lib/libfuse.la

/usr/lib/libulockmgr.la
/usr/lib/libfuse.la
/usr/lib/libulockmgr.so.1.0.1

/usr/lib/libulockmgr.a
/usr/lib/libfuse.a

/usr/lib/libfuse.so.2.8.4


/etc/udev/rules.d/99-fuse.rules
/usr/lib/pkgconfig/fuse.pc
/sbin/mount.fuse
/etc/init.d/fuse

/usr/bin/ulockmgr_server
/usr/bin/fusermount

%post
cd /usr/lib && { ln -s -f libfuse.so.2.8.4 libfuse.so.2 || { rm -f libfuse.so.2 && ln -s libfuse.so.2.8.4 libfuse.so.2; }; }
cd /usr/lib && { ln -s -f libfuse.so.2.8.4 libfuse.so || { rm -f libfuse.so && ln -s libfuse.so.2.8.4 libfuse.so; }; }
cd /usr/lib && { ln -s -f libulockmgr.so.1.0.1 libulockmgr.so.1 || { rm -f libulockmgr.so.1 && ln -s libulockmgr.so.1.0.1 libulockmgr.so.1; }; }
cd /usr/lib && { ln -s -f libulockmgr.so.1.0.1 libulockmgr.so || { rm -f libulockmgr.so && ln -s libulockmgr.so.1.0.1 libulockmgr.so; }; }
ln -s /usr/lib/pkgconfig/fuse.pc /usr/lib64/pkgconfig/fuse.pc

export PKG_CONFIG_PATH=/usr/lib/pkgconfig
ldconfig -n /usr/lib
modprobe fuse
