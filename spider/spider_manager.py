
from __future__ import absolute_import
import config
from utils import object_form_class_name

class SpiderManager(object):


    def __init__(self):
        self.spiders = {}
        confs = config.SPIDER
        for spider_conf in confs:
            if spider_conf['enabled']:
                o = object_form_class_name(spider_conf['class'])
                o.init_pipeline(spider_conf['pipelines'])
                self.spiders[spider_conf['name']] = o

    def run(self):
        for spider in self.spiders.values():
            spider.run()

    def run_spider(self, name):
        if self.spiders.has_key(name):
            self.spiders[name].run()


