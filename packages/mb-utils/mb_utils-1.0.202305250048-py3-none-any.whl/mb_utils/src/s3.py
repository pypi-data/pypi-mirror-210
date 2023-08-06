##file for s3 download and upload

import boto3
import os
from .logging import logger

__all__ = ['download_file', 'upload_file', 'upload_dir', 'download_dir']

def download_file(bucket_name, file_name, local_file_name):
    """
    download file from s3
    Input:
        bucket_name: name of the bucket
        file_name: name of the file in s3
        local_file_name: name of the file in local
    Output:
        None
    """
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket_name).download_file(file_name, local_file_name)
    except Exception as e:
        if logger:
            logger.error('Error in downloading file from s3')
            logger.error(e)
        raise e
    if logger:
        logger.info('Downloaded file from s3')

def upload_file(bucket_name, file_name, local_file_name):
    """
    upload file to s3
    Input:
        bucket_name: name of the bucket
        file_name: name of the file in s3
        local_file_name: name of the file in local
    Output:
        None
    """
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket_name).upload_file(local_file_name, file_name)
    except Exception as e:
        if logger:
            logger.error('Error in uploading file to s3')
            logger.error(e)
        raise e
    if logger:
        logger.info('File uploaded to s3')

def upload_dir(bucket_name, dir_name, local_dir_name):
    """
    upload directory to s3
    Input:
        bucket_name: name of the bucket
        dir_name: name of the directory in s3
        local_dir_name: name of the directory in local
    Output:
        None
    """
    s3 = boto3.resource('s3')
    try:
        for root, dirs, files in os.walk(local_dir_name):
            for file in files:
                s3.Bucket(bucket_name).upload_file(os.path.join(root,file),bucket_name,dir_name)
    except Exception as e:
        if logger:
            logger.error('Error in uploading directory to s3')
            logger.error(e)
        raise e
    if logger:
        logger.info('Directory uploaded to s3')

def download_dir(bucket_name, dir_name, local_dir_name=None):
    """
    download directory from s3
    Input:
        bucket_name: name of the bucket
        dir_name: name of the directory in s3
        local_dir_name: name of the directory in local
    Output:
        None
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        for obj in bucket.objects.filter(Prefix=local_dir_name):
            target = obj.key if local_dir_name is None \
                else os.path.join(local_dir_name, os.path.relpath(obj.key, dir_name))
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if obj.key[-1] == '/':
                continue
            bucket.download_file(obj.key, target)
    except Exception as e:
        if logger:
            logger.error('Error in downloading directory from s3')
            logger.error(e)
        raise e
    if logger:
        logger.info('Downloaded directory from s3')