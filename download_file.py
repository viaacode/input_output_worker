#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 10:58:50 2018
example:
    download_file('http://some.file.mp4','/home/tina/833mw3j63t.mxf').dwnl()
@author: tina
"""

import sys
sys.path.insert(0,'..')
import requests
import shutil
import logging
import configparser
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


LOGGER = logging.getLogger(__name__)
LOG_FORMAT = ('%(asctime)-15s %(levelname) -8s %(name) -10s %(funcName) '
              '-20s %(lineno) -5d: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

config = configparser.ConfigParser()
config.read('config/config.ini')


class download_file(object):
    def __init__(self, url, file,user=None, passwd=None):
        self.url = url
        self.file = file
        self.user = user
        self.passwd = passwd

    def dwnl(self):
        proxies = {
          'http': config['proxy']['url'],
          'https': config['proxy']['url'],
        }
        if self.user is None  and self.passwd is None:
            r = requests.get(self.url, stream=True,proxies=None)
            if r.status_code == 200:
                LOGGER.info('starting download: {}'.format(self.url))
                with open(self.file, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                    
            return self.file 
        else:
            r = requests.get(self.url, auth=HTTPBasicAuth(self.user, self.passwd))
            LOGGER.info('using requests with basic auth ')
           # r = requests.get(self.url, stream=True,proxies=None)
            if r.status_code == 200:
                LOGGER.info('starting download: {}'.format(self.url))
                with open(self.file, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                    
            return self.file 

# print(download_file('http://archief-media.viaa.be/viaa/VRT/ae1263f73cbf41cdbf9efdbb3db82e17a68599ede30249ddaab5359a8da96277/browse.mp4',
#                     '/home/tina/707wm2h60b.mp4',user='ddd',passwd='00').dwnl())