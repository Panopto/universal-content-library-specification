import argparse
import os.path
import hashlib
import boto
import boto3
import re
from botocore.errorfactory import ClientError
from boto.s3.connection import S3Connection


def get_file_from_s3(aws_access_key,
                     aws_secret_key,
                     aws_region,
                     local_path,
                     bucket_name,
                     key_prefix):
    '''
    Syncs files from s3.
    '''
    if (not local_path) or (not bucket_name) or (not key_prefix):
        raise Exception(
           'local_path [{0}],'
           'bucket_name [{1}],'
           'key_prefix [{2}],'
           'are required.'.format(
                local_path,
                bucket_name,
                key_prefix
                ))

    if aws_access_key is None or aws_secret_key is None:
        s3 = boto3.client('s3')  # use the default AWS CLI profile
    else:
        session = boto3.session.Session(region_name=aws_region)
        s3 = session.client('s3',
                            config=boto3.session.Config(
                                signature_version='s3v4'),
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key)

    s3.download_file(bucket_name, key_prefix, local_path)


def directory_exists(bucket_name, key_prefix):
    print("Not yet implemented")


def file_exists(aws_access_key,
                aws_secret_key,
                aws_region,
                bucket_name,
                key_prefix):
    """
    Checks if a S3 key exists
    """
    exists = True
    if aws_access_key is None or aws_secret_key is None:
        s3 = boto3.client('s3')  # use the default AWS CLI profile
    else:
        session = boto3.session.Session(region_name=aws_region)
        s3 = session.client(
            's3',
            config=boto3.session.Config(signature_version='s3v4'),
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
            )

    try:
        s3.head_object(Bucket=bucket_name, Key=key_prefix)
    except ClientError:
        exists = False

    return exists
