# Igneous 101


## Overview

The goal of this lab exercise is to get you familiar with accessing your on premises Igneous Data Service, so that you can :

* ingest data using a variety of tools
* Understand the enhanced metadata capabilities of an ObjectStore




## Pre-req's

**Windows users**: navigate to [Prereq's](prereqs/windows_prereqs.md)

**Mac & Linux users**: navigate to [Prereq's](prereqs/mac_linux_prereqs.md)

***Note: you can also grab all of the doc's and downloadable software prereq's from one of the USB keys floating around the room.***


## Labs

* [S3cmd](labs/s3cmd.md)
* [Python](labs/python.md)


# appendix

## overall plan
* ryan's preso
* setup CLI pre-req's
* break
* s3cmd
* python
* Cyberduck : s3browser?




##stuff to add

* put vcard in pre-created buckets
* backup utility? (cloudBerry , etc)
* s3browser
* cut/paste in community
* install atom ?
* survey at the end
* put everything into community.
* s3cmd workaround to fix cyberduck issue

##Python
* connect
* list_bucket
* list_keys
* upload
* download
* sync (aka: single-threaded os.walk + upload)

* bonus -> more advanced stuff, maybe multi-threaed, etc
* bonus -> crawler that can write to us? pull images, etc..
* copy one of their project mounts, sync that to their bucket (multi-threaded)
