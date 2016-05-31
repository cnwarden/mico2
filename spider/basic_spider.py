from utils.logger import logger

class BasicSpider(object):

    def __init__(self, name):
        logger.info('construct spider:%s' % (name))
        pass

    def run(self):
        pass