#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 14:47:18 2019

@author: tina
"""

import logging
import boto3
import botocore
from download_file import download_file
LOG_FORMAT = ('[%(asctime)-15s: %(levelname)s/%(name)s] %(funcName)s ' +\
                '%(lineno)-4d: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOG_FORMAT = ('[%(asctime)-15s: %(levelname)s/%(name)s] %(funcName)s ' +\
                '%(lineno)-4d: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)


def get_s3(access_key, secret_key, server, bucket, key, dest_path):
    """Downloads a file from a bucket"""
    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=server,
    )

    try:

        url = s3_client.generate_presigned_url(
            'get_object', {'Bucket': bucket, 'Key': key})
        LOGGER.info('generated download link %s', url)

        download_file(url, dest_path).dwnl()

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
