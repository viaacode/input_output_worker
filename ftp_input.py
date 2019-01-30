#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 16:22:25 2019

@author: tina
"""
import os.path as path
import ftplib
import logging

LOGGER = logging.getLogger(__name__)
LOG_FORMAT = ('%(asctime)-15s %(levelname) -8s %(name) -10s %(funcName) '
              '-20s %(lineno) -5d: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

def ftp_get(server,user,passwd,file,destPath):
    """
    - ftp a File to a destFile 
    
    - args
       server,user,passwd,file,destPath
    - returns destination path on local filesystem 
    - example
        ftp_get(server='ftp.DOMAIN',user='USER',passwd='xxxx',
            file='/export/home/OR-w66976m/incoming/0fa62900-87ed-43bb-8189-2ed7eb472d35_86687474-051f-11e9-9cfc-000e1e7c4442.1.mp4',
            destPath='ftpfile')
    """
    _path,lfile = path.split(file)
    ftp = ftplib.FTP(server)
    ftp.login(user, passwd)
    try:
        
        LOGGER.info('starting ftp download {}'.format(file))
        ftp.retrbinary("RETR " + file ,
                       open( destPath, 'wb').write)
        LOGGER.info('file downloaded to {}'.format(destPath))
        return destPath
    except Exception as e:
        LOGGER.error(str(e))

#ftp_get()