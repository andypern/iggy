#!/usr/local/bin/python

import argparse
import boto3
import os
import sys
import time
import threading

def blockify(igneous, key_prefix, file_path, block_size, start_block_id, end_block_id):
    print("Uploading blocks #{}-{}".format(start_block_id, end_block_id))
    session = boto3.session.Session()
    if igneous:
        s3_client = session.client(
            "s3",
            aws_access_key_id=,
            aws_secret_access_key=,
            endpoint_url="http://10.16.28.10:80",
            use_ssl=False,
            verify=False,
            config=boto3.session.Config(
                signature_version="s3",
                connect_timeout=60,
                read_timeout=60,
                s3={"addressing_style": "path"})
        )
        bucket_name = "newdata"
    else:
        s3_resource = session.resource("s3")
        bucket_name = "hrt-newdata"
        s3_client = s3_resource.meta.client

    data_file = open(file_path, "rb")
    data_file.seek(block_size * start_block_id)

    block_id = start_block_id
    while block_id < end_block_id:
        data = data_file.read(block_size)
        s3_client.put_object(Bucket=bucket_name,
                             Key=key_prefix+"b"+str(block_id),
                             Body=data)
        block_id += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("file")
    parser.add_argument("-b", "--block-size", type=int, dest="block_size", default=65536)
    parser.add_argument("-i", "--igneous", action="store_true", default=False,
                        dest="igneous")
    parser.add_argument("-n", "--num-threads", type=int, dest="num_threads", default=1)
    args = parser.parse_args()

    file_path = args.file
    block_size = args.block_size
    igneous = args.igneous
    num_threads = args.num_threads

    try:
        data_file = open(file_path, "rb")
        num_bytes = os.path.getsize(file_path)
    except:
        print("Cannot open " + file_path + ", exiting")
        sys.exit(1)
    data_file.close()

    num_megabytes = float(num_bytes) / 1024 / 1024
    num_blocks = (num_bytes + block_size - 1) / block_size
    if num_threads > num_blocks:
        num_threads = num_blocks
    print("{} blocks, {} threads".format(num_blocks, num_threads))

    start_time = time.time()

    key_prefix = file_path

    num_blocks_per_thread = (num_blocks + num_threads - 1) / num_threads

    threads = []
    for thread_id in range(num_threads):
        start_block_id = thread_id * num_blocks_per_thread
        end_block_id = start_block_id + num_blocks_per_thread
        if end_block_id > num_blocks:
            end_block_id = num_blocks
        thread = threading.Thread(target=blockify, args=(igneous,key_prefix,file_path,block_size,start_block_id,end_block_id));
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    end_time = time.time()

    print("Throughput: {} MB/s".format(num_megabytes / (end_time - start_time)))
