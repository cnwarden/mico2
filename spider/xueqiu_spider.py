# coding:utf-8

from __future__ import absolute_import
from spider.basic_spider import BasicSpider
from utils.logger import logger, debug_logger
import urllib2
from urllib2 import Request, HTTPError, HTTPCookieProcessor, ProxyHandler
import cookielib
from json.decoder import JSONDecoder
from StringIO import StringIO
import gzip
from processor.common_processor import XueQiuProcessor
import time
import random
import config
import spider.utils


class XueQiuSpider(BasicSpider):

    def __init__(self, name='', instruments=[]):
        super(XueQiuSpider, self).__init__(name)
        self.init_client()
        self.processor = XueQiuProcessor()
        self.processor.init_db_connection()

        self.instrument_list = instruments if instruments else config.STOCK_LIST
        self.current_symbol = None
        self.throttle_page = 5

    def __random_choose_agent(self):
        self.headers['User-Agent'] = spider.utils.get_default_header()
        logger.debug('UserAgent:' + self.headers['User-Agent'])

    def run(self):
        logger.info('spider is running')
        self.access_url('http://xueqiu.com')

        # start query data
        for inst in self.instrument_list:
            self.current_symbol = inst
            logger.info("--->instrument [%s] start" % self.current_symbol)
            self.processor.init_instrument(self.current_symbol)
            is_done = False
            page = 1
            while(page <= self.throttle_page):
                url = 'http://www.xueqiu.com/statuses/search.json?count=20&comment=0&symbol=%s&hl=0&source=all&sort=time&page=%d' \
                                        % (self.current_symbol, page)
                logger.info(url)
                resp = self.access_url(url)
                if resp:
                    if resp.info().get('Content-Encoding') == 'gzip':
                        buf = StringIO(resp.read())
                        f = gzip.GzipFile(fileobj=buf)
                        result = JSONDecoder().decode(f.read())
                        debug_logger.debug(result)
                        if result.has_key('list'):
                            for item in result['list']:
                                is_done = self.processor.process({'raw':item})
                                if is_done:
                                    break
                        else:
                            logger.fatal('probably out of range')
                            is_done = True  # mark as complete
                else:
                    # None means bad request, ignore this symbol
                    logger.fatal('Bad Request, abondon this one')
                    break

                if is_done:
                    break;
                page += 1
            logger.info("--->instrument complete")
            sleep_count = random.randint(1, 5)
            logger.info("sleep count:%d" % (sleep_count))
            time.sleep(sleep_count)

    def init_client(self):
        self.headers = spider.utils.get_default_header()
        spider.utils.get_default_header()

        self.cookie = cookielib.CookieJar()
        proxy_list = {'http':'http://10.40.14.56:8080'}
        proxy = ProxyHandler(proxies=proxy_list)
        self.opener = urllib2.build_opener(HTTPCookieProcessor(cookiejar=self.cookie))
        urllib2.install_opener(self.opener)

    def access_url(self, url):
        try:
            self.__random_choose_agent()
            request = Request(url=url, headers=self.headers)
            resp = urllib2.urlopen(request)
            return resp
        except HTTPError, ex:
            logger.info('access_url, get response error')
            logger.fatal(ex)
            return None
