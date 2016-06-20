

from unittest import TestCase
import spider


class TestSpider(TestCase):

    def setUp(self):
        self.spider = spider.ReferenceSpider()

    def tearDown(self):
        pass

    def testStart(self):
        self.spider.run()
        pass