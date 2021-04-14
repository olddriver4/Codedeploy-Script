#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# auth limeng
# Version python3+
# Mode：pip3 install boto3 psutil requests

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

    response = client.create_deployment(
        applicationName=APPNAME,
        deploymentGroupName=DEPLOYNAME,
        revision={
            'revisionType': 'S3',
            's3Location': {
                'bucket': BUCKET_NAME,
                'bundleType': 'zip',
                'key': PREFIX_NAME + '/' + FILE_NAME
                #'version': '2021-02-20_02',
                #'eTag': '3f92baca7a92b4ebac6e3fc728999b3e'
            }
        },
        deploymentConfigName='CodeDeployDefault.AllAtOnce',
        description='string',
        ignoreApplicationStopFailures=False,
        autoRollbackConfiguration={
            'enabled': True,
            'events': [
                'DEPLOYMENT_FAILURE',
            ]
        }
    )

#运行输入参数
def run_string(APPNAME,DEPLOYNAME):
    client = boto3.client(service_code, aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, region_name=region)

    while True:
        time.sleep(20)

        response = client.get_deployment_group(
            applicationName=APPNAME,
            deploymentGroupName=DEPLOYNAME
        )

        status=response['deploymentGroupInfo']['lastAttemptedDeployment']['status']

        if status == 'Failed' or status == 'Stopped':
            failed_logs="Codedeployment run status [%s], Program exit!" %(status)
            print (failed_logs, flush=True)
            sys.exit(1)

        elif status == 'Succeeded':
            succeeded_logs="Codedeployment run status [%s], Program exit!" %(status)
            print (succeeded_logs, flush=True)
            break
            
        else:
            status_logs="Codedeployment runing status [%s] ..." %(status)
            print (status_logs, flush=True)

if __name__ == '__main__':
    try:
        upload_s3(FILE_NAME,FILE_PATH,BUCKET_NAME,PREFIX)
        
        try:
            create_deployment(FILE_NAME,APPNAME,DEPLOYNAME,BUCKET_NAME,PREFIX_NAME)
            run_string(APPNAME,DEPLOYNAME)
        
        except Exception as e:
            print (e, flush=True)
            sys.exit(1)
            
    except Exception as e:
        print (e, flush=True)
        sys.exit(1)
