#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.testkafkaamqp import kafka_work
import tornado.ioloop
import tornado.web
import json
from lycium.kafka.kafkaWorker import KafkaWorker
from lycium.amqplib import RabbitMQFactory
from loguru import logger


kafka_hosts = ["172.16.28.190:9093","172.16.28.190:9094","172.16.28.190:9095"]
kafka_worker = KafkaWorker(kafka_hosts, private_topic="client23")

# virtual_host = 'my_vhost'
# example_exchange = 'ex.message'
# example_queue = 'example.text'
# example = RabbitMQFactory()
# example.initialize({
#         'host':'localhost',
#         'port':5672, 
#         'username':'admin', 
#         'password':'admin',
#         'virtual_host': virtual_host
#     })
# example.set_tracker_queue_name('tracker.example')
# example.run()



class KafkaHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    async def post(self):
        request_body = self.request.body
        logger.info(request_body)
        resp = await kafka_worker.send(topic="microsvc-demo",message=request_body)
        if resp is not None:
            self.write(resp.body)
        else:
            self.write(b"None")

# class RabbitHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world")

#     async def post(self):
#         request_body = self.request.body
#         resp = await example.query_mq(virtual_host, example_exchange, example_queue, request_body)
#         self.write(resp.body)



def make_app():
    return tornado.web.Application([
        (r"/kafka", KafkaHandler),
        # (r"/rabbit", RabbitHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()