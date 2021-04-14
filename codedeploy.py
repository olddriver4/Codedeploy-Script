#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# auth limeng
# Version python3+
# Mode：pip3 install boto3 requests

import requests
import threading
import boto3,sys,time,os

#auth config
access_key=''
secret_access_key=''
region='cn-northwest-1'
service_s3='s3'
service_code='codedeploy'

#[FILE]
FILE_NAME=os.environ['FILE_NAME_ENV']
FILE_PATH=os.environ['FILE_PATH_ENV'] + FILE_NAME

#[BACKET]
BUCKET_NAME=os.environ['BUCKET_NAME_ENV']
PREFIX=os.environ['PREFIX_ENV'] + '/' + FILE_NAME
PREFIX_NAME=os.environ['PREFIX_ENV']

#[BUILD]
APPNAME=os.environ['APPNAME_ENV']
DEPLOYNAME=os.environ['DEPLOYNAME_ENV']
#BUILD_VERSION=os.environ['BUILD_VERSION_ENV']

#显示进度条
class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0 
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s %s / %s (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size, percentage))
            sys.stdout.flush()

#上传S3
def upload_s3(FILE_NAME,FILE_PATH,BUCKET_NAME,PREFIX):
    s3 = boto3.client(service_s3, aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, region_name=region)

    print ("S3文件正在上传中...", flush=True)

    with open(FILE_PATH,"rb") as f:
        s3.upload_fileobj(f, BUCKET_NAME, PREFIX, Callback=ProgressPercentage(FILE_PATH))

#部署codedeploy
def create_deployment(FILE_NAME,APPNAME,DEPLOYNAME,BUCKET_NAME,PREFIX_NAME):
    client = boto3.client(service_code, aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, region_name=region)
    
    print ("\nCodedeployMent 正在运行中...", flush=True)

