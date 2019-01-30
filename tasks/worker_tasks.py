#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORKERS stuff
Created on Fri Nov  3 13:58:25 2017
CELERY TASKS definations
  Note: fake=True variables to pass true to keep One chain
@author: tina
"""
import sys
sys.path.insert(0, '..')
from datetime import datetime, timedelta
#import smtplib
import os
import time
import json
from ftp_input import ftp_get
from celery import Celery, current_task
from download_browse import download_browse
from download_file import download_file
import celeryconfig
from mailer_call import mailer
from celery.utils.log import get_task_logger
from shutil import rmtree
from super_makedirs import make_dir
from result_publisher import pubMsg
import zipfile
from os.path import join, relpath
from kombu import Exchange, Queue
app = Celery('tasks',)
app.config_from_object(celeryconfig)
logger = get_task_logger(__name__)
app = Celery('tasks',)
app.config_from_object(celeryconfig)
app.conf.task_queues = (Queue('transfer_worker',
                              Exchange('transfer_worker'),
                              routing_key='transfer_worker'),)
app.conf.task_default_queue = 'transfer_worker'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'transfer_worker'
app.conf.task_routes = {'tasks.worker_tasks.*': {'queue': 'transfer_worker',
                                                 'routing_key': 'transfer_worker', }, }


@app.task(bind=True)
def get_fake(self, file):
    try:

        os.path.isfile(file)
        time.sleep(1)
        return file
    except Exception as e:
        logger.error(str(e))
        raise self.retry(coutdown=60*5, exc=e, max_retries=5)


# @app.task(rate_limit='5/h')


@app.task(bind=True)
def ftp_result(self, file, destfile, server, user, passwd, ftp_fake=False):
    if ftp_fake:
        return file
    import ftplib
    file = os.path.abspath(file)
    f = open(file, 'rb')
    ftp = ftplib.FTP(server)
    logger.info('Logging in with {} : {}'.format(user, passwd))
    ftp.login(user, passwd)
    ftp.set_pasv(True)
    #  Test to see if the file exists by getting the file size by name.
    #  If a -1 is returned, the file does not exist.
    try:
        size = ftp.size(destfile)
        if size < 0:
            logger.info("file does not exist OK")

        else:
            logger.info("file exists and is " + str(size) + " bytes in size")
            logger.warning('renaming outputfile')

            destfile = os.path.splitext(destfile)[0] + '.1' + os.path.splitext(destfile)[1]
    except Exception as e:
        logger.info(str(e) + 'Not a file will upload')
        pass
    try:
        logger.info('Storing File {} to {}'.format(file, destfile))
        ftp.storbinary('STOR %s' % '{}'.format(destfile), f)
        logger.info('file stored {}'.format(destfile))
        ftp.quit()
        # return '{} @ {}  '.format(destfile, server)
        return destfile
    except Exception as e:
        logger.error(str(e))
        raise self.retry(coutdown=12, exc=e, max_retries=5)


@app.task()
# def send_mail(path, to):
#    # todo **kwargs message body
#    SERVER = "smtp.do.viaa.be"
#    FROM = "support@viaa.be"
#    TO = [to]  # must be a list
#    SUBJECT = "Hi, new file to download!"
#    TEXT = "Your file is ready {}.".format(path)
#    message = 'Subject: %s\n%s' % (SUBJECT, TEXT)
#    server = smtplib.SMTP(SERVER)
#    server.sendmail(FROM, TO, message)
#    server.quit()
#    return 'MAIL sent to {},  {}'.format(TO, TEXT)
def send_mail(path, infile, email):
    mailer(pid=infile, email=email, path=path, export_type='Hires').send()
    return path


@app.task(bind=True)
def resPub(self, msg, user, passw, host, queue, routing_key):
    t_id = current_task.request.id,
    final_msg = json.dumps({'content': msg,
                            'task id': t_id})
    try:
        pubMsg(queue=queue, rabhost=host, user=user,
               passwd=passw, msg=final_msg, routing_key=routing_key).publish()
        return final_msg
    except Exception as e:
        self.retry(coutdown=60*10, exc=e)


@app.task()
def zip_dir(root, zipfilename, **msg):
    """ Zips a dir """
    zipf = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)

    if 'excludes' in msg['service']['zipper']:
        def should_exclude(directory, filename):
            if file == msg['service']['zipper']['dest_filepath']:
                return True
            for exclude in msg['service']['zipper']['excludes']:
                if exclude in directory or exclude in filename:
                    return True
            return False
    else:
        def should_exclude(directory, filename):
            return filename == msg['service']['zipper']['dest_filepath']
    try:
        for directory, subdirs, files in os.walk(root):
            for file in files:
                if should_exclude(directory, file):
                    continue
                arcname = relpath(join(directory, file), root)
                zipf.write(join(directory, file), arcname=arcname)

        zipf.close()
        correlation_id = msg['service']['zipper']['correlation_id']
        out = {'outcome': 'OK',
               'zipfile': zipfilename,
               'correlation_id': correlation_id}

    except Exception as e:
        out = {'outcome': 'NOK',
               'zipfile': zipfilename,
               'correlation_id': correlation_id,
               'ERROR': str(e)}
        raise
    return out


@app.task()
def deleteFile(file):
    # Todo extention filter ,dir length filer (uuid)
    try:
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            rmtree(os.path.abspath(file))
    #        os.rmdir(file)
    except FileNotFoundError as e:
        logger.warning(str(e) + 'file {} was already deleted'.format(file))
    return file


@app.task(bind=True, max_retries=5, default_retry_delay=30)
def transferFromUrl(self, uri, destPath, user=None, password=None):
    try:
        download_file(url=uri,
                      file=destPath,
                      user=user,
                      passwd=password).dwnl()
        return destPath
    except Exception as e:
        self.retry(exc=e, coutdown=30 ** self.request.retries)


@app.task(bind=True, max_retries=5, default_retry_delay=30)
def transferFromFtp(self, host, user, password, path, destpath):
    try:
        ftp_get(server=host, user=user, passwd=password,
                file=path, destPath=destpath)
        logger.info(host)
        return destpath
    except Exception as e:
        self.retry(exc=e, coutdown=30 ** self.request.retries)
