from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from utils.logger import logger
import pytz
from job.spider_jobs import SpiderJob
from db.es import ESWrapper
import config
from datetime import datetime, timedelta

class Manager(object):
    """
    singleton mode
    """
    @classmethod
    def start(cls):
        logger.info('service[job manager] start')
        executors = {
            'default': { 'type': 'threadpool', 'max_workers': 5 }
        }
        jobstores = {
            'default': { 'type': 'memory'}
        }
        cls.bk_scheduler = BackgroundScheduler(logger=logger, timezone=pytz.timezone('Etc/GMT-8'), jobstores=jobstores,
                                               executors=executors)
        cls.bk_scheduler.add_job(func=SpiderJob.run_job, trigger=IntervalTrigger(minutes=15),
                                 # id='1',
                                 name='xueqiu_spider')
        cls.bk_scheduler.add_job(func=SpiderJob.run_top_N, trigger=IntervalTrigger(minutes=60),
                                 name='xueqiu_topN_spider')
        cls.bk_scheduler.start()

    @classmethod
    def get_status(cls):
        status = {'jobs': []}
        jobs = cls.bk_scheduler.get_jobs()
        for job in jobs:
            status['jobs'].append({
                'id': job.id,
                'name': job.name,
                'next_time': job.next_run_time,
            })
        return status

    @classmethod
    def run_job(cls, id):
        job = cls.bk_scheduler.get_job(id)
        next_run = None
        if job:
            next_run = datetime.now(pytz.timezone('Etc/GMT-8')) + timedelta(seconds=10)
            cls.bk_scheduler.modify_job(id, next_run_time=next_run)
        return next_run

    @classmethod
    def test_job(cls):
        SpiderJob.run_job()

    @classmethod
    def run_spider_job(cls, instruments):
        SpiderJob.run_job_one(instruments=instruments)

    @classmethod
    def run_spider_top_N(cls, topN=10):
        client = ESWrapper()
        result = client.get_all_ranks()
        insts = result['code_rank']
        instruments = [inst[0]  for inst in insts if inst[0] not in config.STOCK_LIST]
        N = topN if len(instruments) > topN else len(instruments)
        logger.info(instruments[:N])
        SpiderJob.run_job_one(instruments=instruments[:N])
