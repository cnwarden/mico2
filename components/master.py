# -*- coding: utf-8 -*-


import pytz
import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rq import Queue
import version
from message import HBMessage
from utils.logger import logger
import logging
from job.tasks import crawl, HB
import config


class Master(object):
    """
    Master to generate jobs
    """

    @classmethod
    def connect(cls):
        logger.info("Master is starting")
        logger.info("Version:" + version.VERSION)
        cls.r = redis.Redis.from_url(config.REDIS_URL)
        cls.q = Queue('TQ', connection=cls.r)
        cls.heartbeat = Queue('HB', connection=cls.r)

    @classmethod
    def generate(cls):
        cls.q.enqueue(crawl, args=(1,2,3), kwargs={})

    @classmethod
    def send_heartbeat(cls):
        msg = HBMessage()
        args = msg.get()
        cls.heartbeat.enqueue(HB, args=(), kwargs=args)


    @classmethod
    def run(cls):
        cls.connect()

        lg = logging.getLogger("apscheduler.executors.default")
        lg.addHandler(logging.StreamHandler())

        bk_sche = BackgroundScheduler(logger=logger, timezone=pytz.timezone('Etc/GMT-8'))
        bk_sche.add_job(func=Master.send_heartbeat, trigger=IntervalTrigger(seconds=1))
        bk_sche.start()

        # job generator
        scheduler = BlockingScheduler(logger=logger, timezone=pytz.timezone('Etc/GMT-8'))
        scheduler.add_job(func=Master.generate, trigger=IntervalTrigger(seconds=3))
        scheduler.start()

if __name__ == "__main__":
    Master.run()







