

sudo rm /var/lib/apt/lists/* -vf

sudo apt-get update
sudo apt-get -f install



sudo apt-get install automake autotools-dev g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config


Grab the cherry-picked s3fs-fuse tarball.

./autogen.sh
./configure
make
