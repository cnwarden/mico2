from __future__ import absolute_import
from utils.logger import logger
from pipeline import PipelineManager

class BasicSpider(object):

    def __init__(self, name):
        logger.info('construct spider:%s' % (name))
        self.pm = None

    def init_pipeline(self, pipelines=[]):
        logger.info('loading pipeline')
        self.pm = PipelineManager(pipelines=pipelines)

    def process(self, msg):
        self.pm.process(msg)

    def run(self):
        pass