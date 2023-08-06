#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lycium.kafka.kafkaWorker import KafkaWorker
from loguru import logger
import time
import datetime

kafka_hosts = ["172.16.28.190:9093","172.16.28.190:9094","172.16.28.190:9095"]
topic = "microsvc-demo"

worker = KafkaWorker(
    hosts=kafka_hosts, 
    group_id="microsvc-aaccdd"
)

async def now(request):
    """
    测试用的业务方法
    """
    logger.info(request.body)
    time.sleep(62)
    return {
        "code":0,
        "msg":"success",
        "data":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

worker.subscribe(topic,)