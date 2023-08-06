# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 14:54:00 2021

@author: yqlim
"""
from ast import Call
from typing import Callable, Dict
import pika
import json

import logging
logger = logging.getLogger(__name__)

class RabbitMQ(object):
    def __init__(self) -> None:
        pass

    @classmethod
    def make_task_basic(cls, task_name: str, data: Dict) -> str:
        data['task_name'] = task_name
        return json.dumps(data)
    
    @classmethod
    def join_queue_basic(cls, queue_name: str, body: Dict, host: str = 'localhost') -> None:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=body)
        connection.close()
    
    @classmethod
    def consume_basic(cls, queue_name: str, callback: Callable, auto_acknowledge: bool = True,
                            host: str='localhost', heartbeat: int=900):
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=heartbeat))
                channel = connection.channel()
                channel.queue_declare(queue=queue_name)
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue=queue_name, auto_ack=auto_acknowledge, 
                                        on_message_callback=callback)
                channel.start_consuming()
            except Exception as e:
                msg = 'error at queue ({queue_name}) - {error_message}\nconnection closed...and restarted'.format(
                            queue_name=queue_name, error_message=e)
                logger.error(msg)
                continue


class RabbitCallback(object):
    def __init__(self, ch: pika.adapters.blocking_connection.BlockingChannel, 
                     method: pika.spec.Basic.Deliver, 
                     properties: pika.spec.BasicProperties, 
                     body: bytes) -> None:
        self.ch = ch
        self.method = method
        self.properties = properties
        self.body = body