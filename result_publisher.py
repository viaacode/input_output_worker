#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 09:25:35 2017
Usage:
     msg=json.dumps({'test':'result'})
     pubMsg(queue='test',rabhost='do-tst-rab-01.do.viaa.be',
            user='larrry',
            passwd='cow',
            msg=msg).publish()

@author: tina
"""
import pika
from pika import PlainCredentials
from pika import exceptions
import logging
LOGGER = logging.getLogger(__name__)


class pubMsg(object):
    def __init__(self,queue, rabhost,user,passwd,msg,routing_key='workers'):
        self.queue = queue
        self.host = rabhost
        self.topic_type ='direct'
        self.user = user
        self.passwd=passwd
        self.result_exchange='workersResults'

        self.publish_connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host,
            port=5672,
            virtual_host='/',
            heartbeat_interval=int(0),
            retry_delay=3,
            connection_attempts=60,
            credentials=PlainCredentials(self.user, self.passwd)
        ))
        self.publish_channel = self.publish_connection.channel()
        self.result_routing = routing_key
        self.msg=msg
        self.publish_channel.queue_declare( queue=self.queue, passive=False,
                                           durable=True, exclusive=False,
                                           auto_delete=False)

    def publish(self):
        if self.queue is not None\
                        and self.topic_type is not None:
            self.publish_channel.\
                exchange_declare(exchange='workersResults')

            self.publish_channel.queue_bind(queue=self.queue,
                                            exchange=self.result_exchange,
                                            routing_key=self.result_routing)
            self.publish_channel.basic_publish(exchange=self.result_exchange,
                                               routing_key=self.result_routing,
                                               body=self.msg,
                                               properties=pika.BasicProperties(
                                                            content_type='application/json',
                                                            delivery_mode=1)
                                              )
        logging.info("Message published to: " + self.result_exchange + "/" + self.result_routing)
        logging.info(self.msg)
        self.publish_connection.close()
