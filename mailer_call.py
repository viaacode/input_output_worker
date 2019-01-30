#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 23 14:42:14 2018
Usage: 
    mailer(pid='urfogmhph',path='/dygzeofgd/gduhfguzf/shdgef',
    email='tina.cochet@viaa.be',
    export_type='larry_type').send()  
@author: tina
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import logging
import configparser

LOG_FORMAT = ('[%(asctime)-15s: %(levelname)s/%(name)s] %(funcName)s ' +\
                '%(lineno)-4d: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config/config.ini')
mailerid = config['mailer']['id']
mailer_auth = config['mailer']['mailer_auth']

class mailer(object):
    def __init__(self,pid,path,email,export_type="api_request"):
        self.pid=pid,
        self.path=path,
        self.email=email
        self.export_type=export_type
    def send(self):
        url='https://api.createsend.com/api/v3.2/transactional/smartemail/{}/send'.format(mailerid)

        data={
            "export_type": "{}".format(self.export_type),
            
            "pid": "{}".format(self.pid[0]),
            "export_path": "{}".format(self.path[0])
        }
        to=  ["{}".format(self.email)]
        ConsentToTrack="unchanged"
        dest={'To':to,
              'Data':data,
              'ConsentToTrack':ConsentToTrack
              }
        data=json.dumps(dest)
        logger.info(data)
        r=requests.post(url=url,data=data, auth=(mailer_auth, '.'))
        logger.info('mailer status code: {}'.format(str(r.status_code)))
       
        return r.status_code