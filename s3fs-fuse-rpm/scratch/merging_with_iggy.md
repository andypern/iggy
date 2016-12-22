10170  git clone https://github.com/s3fs-fuse/s3fs-fuse
10171  git remote add iggy git@github.com:igneous-systems/s3fs-fuse.git
10172  pwd
10173  cd s3fs-fuse
10174  git remote add iggy git@github.com:igneous-systems/s3fs-fuse.git
10175  git fetch iggy
10176  git cherry-pick 26538d66187b6d0a208f0f0c001fad4afc4afbca
10177  pwd
10178  git status
10179  vi src/s3fs.cpp
(look for === , clean stuff up)

10180  vi test/integration-test-main.sh
10181  pwd
10182  git checkout -- test/integration-test-main.sh
10183  git status
10184  git rm test/integration-test-main.sh
10185  git add src/s3fs.cpp
10186  git cherry-pick --continue
➜  s3fs-fuse git:(master)
