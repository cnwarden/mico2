# coding:utf-8

"""
main from rqwork
"""

import redis
from rq.worker import Worker
from rq import Queue
import config

conn = redis.Redis.from_url(config.REDIS_URL)
queues = [Queue(q, connection=conn) for q in ['TQ']]
wk = Worker(queues,
            connection=conn)
wk.work(burst=False)