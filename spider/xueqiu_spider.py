# coding:utf-8

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
        idx = random.randint(0, len(self.user_agents)-1)
        self.headers['User-Agent'] = self.user_agents[idx]
        logger.debug('UserAgent:' + self.user_agents[idx])

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
        # chrome, firefox, safari
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
            'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; tr-TR) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; da-dk) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-HK) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5'
        ]
        self.headers = {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,ja;q=0.2,zh-TW;q=0.2',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        }
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
