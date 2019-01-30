#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 10:58:50 2018
example:
    download_browse('833mw3j63t','/home/tina/833mw3j63t.mxf').dwnl()
@author: tina
"""

import sys
sys.path.insert(0,'..')
import json
import os
from requests.auth import HTTPBasicAuth
import requests
import pyjq
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

user = config['mh_rest']['user']
passwd = config['mh_rest']['passwd']

class download_browse(object):
    def __init__(self, pid, file,user=user,passwd=passwd):
        self.pid = pid
        self.file = file
        self.user= user
        self.password=passwd
        
    def dwnl(self):
        url_base='https://do-prd-app-m0.do.viaa.be/mediahaven-rest-api/resources/media/'
        url = url_base + \
        '?q=%2b(MediaObjectFragmentisiningestspace:*' + \
        ' AND MediaObjectExternalId:'
        url = url + self.pid + ')'
        s = requests.Session()
        retries = Retry(total=5, 
                    backoff_factor=1, 
                    status_forcelist=[ 502, 503, 504 ])
        
        s.mount('https://', HTTPAdapter(max_retries=retries)) 
        r = s.get(url, auth=HTTPBasicAuth(user, passwd))
        json_obj = r.json()   
        for item in json_obj:
            itemText = json.dumps(json_obj[item])
            if item == 'totalNrOfResults' and itemText == '0':
                LOGGER.error('{}, No rest response'.format(self.pid))
                """ TODO: add raise and retry """
                return None
            if item == 'totalNrOfResults' and itemText != '0':
                browse_url =  pyjq.first('.mediaDataList[].videoPath',json_obj)

                browse_url= browse_url.replace('https://archief-media.viaa.be',' http://mediahaven.prd.do.viaa.be')

               
        r = requests.get(browse_url, stream=True)
        p,f=os.path.split(self.file)
        path=os.path.join(p,  self.pid + '.mp4')
        if r.status_code == 200:
            LOGGER.info('starting download')
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        return path 



#print(download_browse('707wm2h60b','/tmp/707wm2h60b.mp4').dwnl())