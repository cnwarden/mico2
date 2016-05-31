

from unittest import TestCase
from spider.xueqiu_spider import XueQiuSpider


class TestSpider(TestCase):

    def setUp(self):
        self.spider = XueQiuSpider()

    def tearDown(self):
        pass

    def testStart(self):
        # self.spider.run()
        pass