https://github.com/axboe/fio

apt-get install fio

also look at this:
https://github.com/khailey/fio_scripts


example of using a jobfile:

	fio --timeout 120 --readonly /home/ubuntu/jobfiles/1mrandread


using just CLI:

	fio --name=sample --rw=randread --size=10g --bs=1m --filename=/mnt/ntap/andy/fio/100gb.file --numjobs=4

example output:


```
fio --timeout 120 --readonly /home/ubuntu/jobfiles/1mrandread
job1: (g=0): rw=randread, bs=1M-1M/1M-1M, ioengine=sync, iodepth=1
job2: (g=0): rw=randread, bs=1M-1M/1M-1M, ioengine=sync, iodepth=1
fio 1.59
Starting 2 processes
Jobs: 1 (f=1): [_r] [99.8% done] [80740K/0K /s] [77 /0  iops] [eta 00m:01s]
job1: (groupid=0, jobs=1): err= 0: pid=4691
 read : io=10240MB, bw=22626KB/s, iops=22 , runt=463447msec
   clat (usec): min=260 , max=1339.4K, avg=45248.86, stdev=66381.67
	lat (usec): min=260 , max=1339.4K, avg=45249.23, stdev=66381.71
   bw (KB/s) : min= 1920, max=103413, per=51.97%, avg=23444.34, stdev=17366.83
 cpu          : usr=0.03%, sys=1.51%, ctx=94037, majf=1, minf=281
 IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
	submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
	complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
	issued r/w/d: total=10240/0/0, short=0/0/0
	lat (usec): 500=5.56%, 750=0.12%, 1000=0.02%
	lat (msec): 2=0.03%, 4=0.17%, 10=21.99%, 20=28.54%, 50=15.72%
	lat (msec): 100=14.22%, 250=11.85%, 500=1.62%, 750=0.16%, 1000=0.01%
	lat (msec): 2000=0.01%
job2: (groupid=0, jobs=1): err= 0: pid=4692
 read : io=10240MB, bw=22554KB/s, iops=22 , runt=464919msec
   clat (usec): min=259 , max=1275.3K, avg=45391.92, stdev=66136.58
	lat (usec): min=259 , max=1275.3K, avg=45392.31, stdev=66136.60
   bw (KB/s) : min= 1796, max=103209, per=51.69%, avg=23316.07, stdev=16939.80
 cpu          : usr=0.03%, sys=1.50%, ctx=95499, majf=0, minf=284
 IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
	submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
	complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
	issued r/w/d: total=10240/0/0, short=0/0/0
	lat (usec): 500=5.76%, 750=0.10%
	lat (msec): 4=0.18%, 10=22.16%, 20=27.54%, 50=16.00%, 100=14.52%
	lat (msec): 250=11.94%, 500=1.66%, 750=0.13%, 2000=0.02%

Run status group 0 (all jobs):
  READ: io=20480MB, aggrb=45107KB/s, minb=23095KB/s, maxb=23168KB/s, mint=463447msec, maxt=464919msec

  ```

  for i in 5 6 7 8 9 10
  do
  fio --name=sample --rw=randread --size=1% --runtime=300 --bs=1m --opendir=/mnt/apfio/largefiles/andy/fio --numjobs=${i}  --eta=always | tee -a /home/ubuntu/fio_runs/fio.1tb.1m_bs.${i}j_5mins_run2.txt
  echo 3 > /proc/sys/vm/drop_caches
  done



for i in `seq 4`
do
fio --name=sample --rw=randread --runtime=300 --size=1% --bs=1m --opendir=/mnt/apfio/largefiles/andy/fio --numjobs=${i}  --eta=always | tee -a /home/ubuntu/fio.1tb.1m_bs.${i}j_300s.txt
echo 3 > /proc/sys/vm/drop_caches
done

for i in `seq 4`
do
fio --name=sample --rw=randread --size=1% --bs=1m --opendir=/mnt/apfio/largefiles/andy/fio --numjobs=${i}  --eta=always | tee -a /home/ubuntu/fio_runs/fio.1tb.1m_bs.${i}j_1pct.txt
echo 3 > /proc/sys/vm/drop_caches
done

 fio --name=sample --rw=randread --size=1% --bs=1m --opendir=/mnt/apfio/largefiles/andy/fio --numjobs=1  --eta=always

for i in 8 9 10 11 12 13 14 15
do
 fio --name=bstor --rw=randread --size=10% --bs=1m --opendir=/mnt/bstors4/fio --numjobs=${i} --eta=always --runtime=300 | tee -a /home/ubuntu/fio_runs/bstor_2mb.100gb.1m_bs_${i}j_5mins_run5.txt
 echo 3 > /proc/sys/vm/drop_caches
 done



 for i in 8 9 10 11 12 13 14 15
 do
  fio --name=bstor --rw=randread --size=10% --bs=1m --opendir=/mnt/bstors4/fio --numjobs=${i} --eta=always --runtime=300 | tee -a /home/ubuntu/fio_runs/bstor_2mb.100gb.1m_bs_${i}j_5mins_run2.txt
  echo 3 > /proc/sys/vm/drop_caches
  done


   for i in `seq 8`
   do
    fio --name=goofy --rw=randread --size=10% --bs=1m --opendir=/mnt/goofy/largefiles/andy/fio --numjobs=${i} --eta=always --runtime=300 | tee -a /home/ubuntu/fio_runs/goofy.1m_bs_${i}j_5mins_run1.txt
    echo 3 > /proc/sys/vm/drop_caches
    done

	for i in `seq 16`
    do
     fio --name=goofy --rw=randread --bs=1m --opendir=/mnt/goofy/largefiles/andy/fio --numjobs=${i} --eta=always --runtime=120 | tee -a /home/ubuntu/fio_runs/goofy.1m_bs_${i}j_2mins_run1.txt
     echo 3 > /proc/sys/vm/drop_caches
     done

fio --name=goofy --rw=randread --bs=1m --opendir=/mnt/goofy/largefiles/andy/fio --numjobs=16 --eta=always --runtime=600 | tee -a /home/ubuntu/fio_runs/goofy.1m_bs_16j_10mins_run1.txt

## 1MB files

for i in `seq 16`
do
 fio --name=goofy --rw=randread --bs=1m --opendir=/mnt/goofy/1M100k --numjobs=${i} --eta=always --runtime=60 | tee -a /home/ubuntu/fio_runs/goofy.1mbfiles_1m_bs_${i}j_1min_run3.txt
 echo 3 > /proc/sys/vm/drop_caches
 done


## s3


	 for i in `seq 16`
     do
      fio --name=goofy --rw=randread --size=10% --bs=1m --opendir=/mnt/goofy --numjobs=${i} --eta=always --runtime=300 | tee -a /home/ubuntu/fio_runs/aws_goofy.1m_bs_${i}j_5mins_run2.txt
      echo 3 > /proc/sys/vm/drop_caches
      done

#das


	  for i in `seq 4`
      do
       fio --name=goofy --rw=randread --size=10% --bs=1m --opendir=/bigdisk/fio --numjobs=${i} --eta=always --runtime=300 | tee -a /home/ubuntu/fio_runs/bigdisk_goofy.1m_bs_${i}j_5mins_run1.txt
       echo 3 > /proc/sys/vm/drop_caches
       done


# s3proxy (+ SSD)


	for i in `seq 16`
    do
     fio --name=goofy --rw=randread --size=10% --bs=1m --opendir=/mnt/proxy --numjobs=${i} --eta=always --runtime=120 | tee -a /home/ubuntu/fio_runs/proxy_goofy.1m_bs_${i}j_5mins_run1.txt
     echo 3 > /proc/sys/vm/drop_caches
     done


# ram


 fio --name=ram --rw=randread --size=10% --bs=1m --opendir=/dev/shm --numjobs=1 --eta=always --runtime=30 | tee -a /home/ubuntu/fio_runs/ramdisk_4GBfile.txt
