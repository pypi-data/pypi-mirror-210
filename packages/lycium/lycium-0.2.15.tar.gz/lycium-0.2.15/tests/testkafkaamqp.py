#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
测试同时使用kafka 订阅topic 和 rabbit 接收信息时是否会阻塞
"""
import json
import datetime
import time
from tornado.ioloop import IOLoop
import tornado.gen

from lycium.kafka.kafkaWorker import KafkaWorker
from lycium.amqplib import RabbitMQFactory


kafka_hosts = ["localhost:9092","localhost:9093","localhost:9094"]

async def kafka_work(message):
    """ """
    value = message.payload
    print(value)
    value = json.loads(value)
    value["reply"]="reply from kafka {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return json.dumps(value)

@tornado.gen.coroutine
def test_callback(unused_channel, basic_deliver, properties, body):
    #time.sleep(0.5)
    print('== on message consumer_tag:%s delivery_tag:%s' % (basic_deliver.consumer_tag, basic_deliver.delivery_tag), body)
    #return 'Response: ' + str(body)
    value = json.loads(body)
    value["reply"]="reply from rabbit {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return json.dumps(value)



def run():
    # 启动订阅kafka topic
    # kafak_worker = KafkaWorker(kafka_hosts,private_topic="server11")
    # kafak_worker.subscribe("test",kafka_work)

    # 启动接收rabbit 信息
    virtual_host = 'my_vhost'
    example_exchange = 'ex.message'
    example_queue = 'example.text'


    example = RabbitMQFactory()
    example.initialize({
        'host':'10.2.11.225',
        'port':5672, 
        'username':'admin', 
        'password':'admin',
        'virtual_host': virtual_host
    })
    example.set_tracker_queue_name('tracker.example')
    example.consume(virtual_host, example_exchange, 'topic', example_queue, example_queue, False, test_callback)
    example.run()

    IOLoop.instance().start()

if __name__ == "__main__":
    run()