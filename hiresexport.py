#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 17:07:24 2017

@author: tina

TODO encrypt passwd??
example:
    download_hires('833mw3j63t','/home/tina/833mw3j63t.mxf').dwnl()
"""

import sys
sys.path.insert(0,'..')
import json
import time
from requests.auth import HTTPBasicAuth
import requests
import pyjq
import shutil
import logging
import configparser

LOGGER = logging.getLogger(__name__)
LOG_FORMAT = ('%(asctime)-15s %(levelname) -8s %(name) -10s %(funcName) '
              '-20s %(lineno) -5d: %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

config = configparser.ConfigParser()
config.read('config/config.ini')

user = config['mh_rest']['user']
passwd = config['mh_rest']['passwd']

class download_hires(object):
    def __init__(self, pid, file,user=user,passwd=passwd):
        self.pid = pid
        self.file = file
        self.user= user
        self.password=passwd
    def dwnl(self):
        objid = get_request(self.pid, short=True,user=self.user,
                            passwd=self.password)
        exportId = request_mh_export(objid,user=self.user,
                            passwd=self.password)
        url = export_poll_status(exportId,user=self.user,
                            passwd=self.password)
        LOGGER.info('mh_auth {}:{} '.format(self.user,self.password))
        dwnl(url, self.file)

# Use short to get mediaObjectId
def get_request(pid, short=False, videoPath=False,user=user,passwd=passwd):
    base_url = 'https://do-prd-app-m0.do.viaa.be/mediahaven-rest-api'
    url = base_url + '/resources/media/?q=%2b(MediaObjectExternalId:'
    url = url + pid + ')'
    try:
        r = requests.get(url, auth=HTTPBasicAuth(user, passwd))
        json_obj = r.json()
        for item in json_obj:
            itemText = json.dumps(json_obj[item])
            if item == 'totalNrOfResults' and itemText == '0':
                LOGGER.error('Failure: NO rest response for {}'.format(pid))
            if item == 'totalNrOfResults' and itemText != '0':
                LOGGER.info('Success: rest response for {}'.format(pid))
            if item == 'mediaDataList':
                    o = pyjq.first(
                        '.mediaDataList[]', json_obj)
                    LOGGER.info(o)
                    PID = pyjq.first(
                        '.mediaDataList[].mdProperties[] |'
                        ' select(.attribute|contains("PID")).value', json_obj)
                    lores = pyjq.first(
                        '.mediaDataList[].videoPath', json_obj)
                    fragment_id = pyjq.first(
                        '.mediaDataList[].fragmentId', json_obj)
                    mediaObjectId = pyjq.first(
                        '.mediaDataList[].mediaObjectId', json_obj)
                    if short is True:
                        if not videoPath:
                            return mediaObjectId
                        else:
                            return lores
                    else:
                        return {'pid': PID,
                                'fragmentid': fragment_id,
                                'mediaObjectId': mediaObjectId,
                                'videopath': lores
                                }
    except Exception as e:
        return str(e)

# schedule export
def request_mh_export(mediaObjectId,user=user,passwd=passwd):
    base_url = 'https://do-prd-app-m0.do.viaa.be/mediahaven-rest-api'
    url = base_url + '/resources/media/{}/export'.format(mediaObjectId)
    try:
        r = requests.post(url, auth=HTTPBasicAuth(user, passwd))
        LOGGER.info('rest request status code: ' + str(r.status_code))
        json_obj = r.json()
        LOGGER.info(json_obj)
        exportid = pyjq.first('.[].exportId', json_obj)
    except Exception as e:
        LOGGER.error(str(e))
    return exportid


def check_export_status(exportid,user=user,passwd=passwd):
    base_url = 'https://dg-prd-app-m0.dg.viaa.be/mediahaven-rest-api'
    try:
        url = base_url + '/resources/exports/' + exportid
        r = requests.get(url, auth=HTTPBasicAuth(user, passwd),verify=False)
        LOGGER.info(r.text)
        json_obj = r.json()
        status = pyjq.first(
                    '.[].status', json_obj)
        downloadUrl = pyjq.first(
                    '.[].downloadUrl', json_obj)
        response = status, downloadUrl
        LOGGER.info('export status: {}'.format(response))
        return response

    except Exception as e:
        LOGGER.error(str(e))


def export_poll_status(exportid,user=user,passwd=passwd):
    while True:
        r = check_export_status(exportid,user=user,passwd=passwd)
        if r[1] == '':
            time.sleep(50)
            LOGGER.info('file not ready yet')
        else:
            LOGGER.info('file can be downloaded from {}'.format(r[1]))
            f = 'https://do-prd-app-m0.do.viaa.be/' + \
                r[1].split('https://archief.viaa.be/',1)[1]
            LOGGER.info('file can be downloaded from {}'.format(f))
            # return the local url
            return f


def dwnl(url, file):
    try:
        # TODO add certificate and drop verify=False
        r = requests.get(url, stream=True, verify=False)
        if r.status_code == 200:
            with open(file, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        LOGGER.info('File downloaded {}'.format(file))
        return True
    except Exception as e:
        LOGGER.error(str(e))

def download(self, url, name):
    request = self.client.get(url, stream=True, verify=False)

    with open(name, "wb") as code:
        for chunk in request.iter_content(1024):
            if not chunk:
                break
            code.write(chunk)
    
#download_hires(pid='4b2x35v74h', user='viaa@testbeeld',passwd='viatweeduusd33$',file='/home/tina/8911n94k73.mp4').dwnl()