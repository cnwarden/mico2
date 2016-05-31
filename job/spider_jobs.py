from spider.xueqiu_spider import XueQiuSpider
from utils.logger import logger
import config
from db.es import ESWrapper

class SpiderJob(object):

    @classmethod
    def run_job(cls):
        spider = XueQiuSpider(name='XueQiu', instruments=config.STOCK_LIST)
        try:
            spider.run()
        except Exception, ex:
            logger.warn('spider run exception')
            logger.fatal(ex)

    @classmethod
    def run_job_one(cls, instruments=[]):
        spider = XueQiuSpider(name='XueQiu', instruments=instruments)
        try:
            spider.run()
        except Exception, ex:
            logger.warn('spider run exception')
            logger.fatal(ex)

    @classmethod
    def run_top_N(cls):
        topN = 10
        client = ESWrapper()
        result = client.get_all_ranks()
        insts = result['code_rank']
        instruments = [inst[0]  for inst in insts if inst[0] not in config.STOCK_LIST and (inst[0][:2] == 'SH' or inst[0][:2] == 'SZ')]
        N = topN if len(instruments) > topN else len(instruments)
        logger.info('before top N')
        logger.info(config.STOCK_LIST)
        SpiderJob.run_job_one(instruments=instruments[:N])
        config.STOCK_LIST += instruments[:N]
        config.STOCK_LIST = config.STOCK_LIST[:30] # keep a small collections
        logger.info('after top N')
        logger.info(config.STOCK_LIST)
