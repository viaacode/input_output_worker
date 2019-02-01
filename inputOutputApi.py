#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 13 14:45:07 2018
TODO cleanup
@author: tina
"""
import os
import uuid
import logging
import configparser
from datetime import datetime, timedelta
from celery import chain
from celery.utils.log import get_logger
from tasks.worker_tasks import ftp_result, send_mail, resPub,\
                               deleteFile, transferFromUrl, transferFromFtp
import connexion

LOG_FORMAT = ('%(asctime)-15s %(levelname) -8s %(name) -10s %(funcName) '
              '-20s %(lineno) -5d: %(message)s')

logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
LOGGER = get_logger(__name__)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = configparser.ConfigParser()
CONFIG.read('config/config.ini')


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def create_job(**body):
    """
    This function creates a new Transfer job.
    TODO add some logic
    """
    msg = body['body']
    tempfile = 'temp/' + str(uuid.uuid1())

    def _in():
        if 'http' in msg['input']['type']:
            LOGGER.info(msg['input']['type']['http'])
            _input = 'fromUrl'
            return msg['input']['type']['http'], _input
        if 'ftp' in msg['input']['type']:
            _input = 'fromFtp'
            return msg['input']['type']['ftp'], _input

    def _out():
        if 'filesystem' in msg['output']['type']:
            _output = 'toFilesystem'
            return msg['output']['type']['filesystem'], _output
        if 'ftp' in msg['output']['type']:
            _output = 'toFtp'
            return msg['output']['type']['ftp'], _output
    i = _in()[0]
    o = _out()[0]
    worker_msg = merge_two_dicts(i, o)
    # worker_msg = {**_in()[0], **_out()[0]}
    _input = _in()[1]
    _output = _out()[1]
    LOGGER.info(worker_msg)
    if _output == 'toFilesystem':
        LOGGER.info('output set to filesystem path')
    if _output == 'toFtp':
        LOGGER.info('output set to ftp')
#  worker logic comes here
#  Todo refactor to something useful
    if _input == 'fromUrl' and _output == 'toFilesystem':
        if 'user' in worker_msg and 'passwd' in worker_msg:
            job = transferFromUrl.s(uri=worker_msg['uri'],
                                    destPath=worker_msg['destPath'],
                                    user=worker_msg['user'],
                                    password=worker_msg['passwd'])
            task = job.apply_async(retry=True)
            job_id = task.id
        else:
            job = transferFromUrl.s(uri=worker_msg['uri'],
                                    destPath=worker_msg['destPath'])
            task = job.apply_async()
            job_id = task.id
        worker_msg['job_id'] = job_id
        return worker_msg
    if _input == 'fromFtp' and _output == 'toFilesystem':
        job = transferFromFtp.s(password=worker_msg['passwd'],
                                host=worker_msg['host'],
                                user=worker_msg['user'],
                                path=worker_msg['path'],
                                destpath=worker_msg['destPath'])
        task = job.apply_async(retry=True)
        job_id = task.id
        worker_msg['job_id'] = job_id
        return worker_msg
    if _input == 'fromFtp' and _output == 'toFtp':
        job = chain(transferFromFtp.s(password=worker_msg['passwd'],
                                      host=worker_msg['host'],
                                      user=worker_msg['user'],
                                      path=worker_msg['path'],
                                      destpath=tempfile),
                    ftp_result.s(server=worker_msg['ftpHost'],
                                 destfile=worker_msg['ftpPath'],
                                 user=worker_msg['ftpUser'],
                                 passwd=worker_msg['ftpPasswd']))
        task = job.apply_async(retry=True)
        job_id = task.id
        worker_msg['job_id'] = job_id
        delta_time = datetime.utcnow() + timedelta(days=1)
        LOGGER.info('scheduled deletion of %s in 1 day', tempfile)
        deleteFile.apply_async((tempfile,), eta=delta_time)
        return worker_msg
    if _input == 'fromUrl' and _output == 'toFtp':
        if 'user' in worker_msg and 'passwd' in worker_msg:
            job = chain(transferFromUrl.s(uri=worker_msg['uri'],
                                          user=worker_msg['user'],
                                          password=worker_msg['passwd'],
                                          destPath=tempfile),
                        ftp_result.s(server=worker_msg['ftpHost'],
                                     destfile=worker_msg['ftpPath'],
                                     user=worker_msg['ftpUser'],
                                     passwd=worker_msg['ftpPasswd']))
        else:
            job = chain(transferFromUrl.s(uri=worker_msg['uri'],
                                          destPath=tempfile),
                        ftp_result.s(server=worker_msg['ftpHost'],
                                     destfile=worker_msg['ftpPath'],
                                     user=worker_msg['ftpUser'],
                                     passwd=worker_msg['ftpPasswd']))
        task_chain = job.apply_async(retry=True)
        job_id = task_chain.id
        worker_msg['job_id'] = job_id
        delta_time = datetime.utcnow() + timedelta(days=1)
        LOGGER.info('scheduled deletion of %s in 1 day', tempfile)
        deleteFile.apply_async((tempfile,), eta=delta_time)
        return worker_msg


APP = connexion.FlaskApp('api', specification_dir='swagger/api')
APP.add_api('py_api.yaml', arguments={'title': 'Transfer API'})


if __name__ == '__main__':
    APP = connexion.FlaskApp(__name__,
                             port=9090,
                             specification_dir='swagger/api')
    APP.add_api('py_api.yaml',
                arguments={'title': 'Transfer API'})
    APP.run()
