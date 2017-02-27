# S3fs-fuse RPMS
To make life a little easier, we've pre-built RPMs for s3fs-fuse.

Note that in the case of `RHEL5` and `RHEL6` , you will also need to install a pre-built `fuse` RPM, as the version of fuse shipping with those distributions is too old `(<2.8.4)`.  `RHEL7` does not have this issue, as the version of fuse currently shipping with that distribution is `>=2.9`.

***Be sure to use the instructions associated with your version of linux.***

*  [RHEL5](RHEL5/README.md)
*  [RHEL6](RHEL6/README.md)
*  [RHEL7](RHEL7/README.md)
