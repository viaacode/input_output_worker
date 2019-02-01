# -*- coding: utf-8 -*-
"""
Configuration for celery work queue
"""
import os
import configparser
## get config 
config = configparser.ConfigParser()
config.read('config/config.ini')
#if 'BROKER_URL' in os.environ:
#    broker_url = os.environ.get('BROKER_URL')
#    print(broker_url)
#else:
#    broker_url = config['Celery']['broker_url'] 
broker_url = config['Celery']['broker_url'] 
result_backend = 'elasticsearch://dg-prd-lst-01.dg.viaa.be:9200/inoutworker-ftp/results'

#result_backend = 'elasticsearch://do-tst-lst-01.do.viaa.be:9200/transcoder/results'
#result_backend = 'rpc://'
# sqlite (filename)
#dbfile = os.path.abspath('results.sqlite')
#result_backend = 'db+sqlite:///results.sqlite'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
#timezone = 'Europe/Brussels'
enable_utc = True
result_persistent = True
