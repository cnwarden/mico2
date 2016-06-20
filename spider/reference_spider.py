# coding:utf-8

from __future__ import absolute_import
from spider.basic_spider import BasicSpider
import spider
import urllib
import urllib2
import json
from utils.logger import logger

"""
reference url:
http://quotes.money.163.com/hs/service/marketradar_ajax.php?page=0&query=STYPE%3AEQA&types=&count=28&type=query&order=desc
query string:
page:0
query:STYPE:EQA
types:
count:28
type:query
order:desc

沪深A股:EQA
沪市A股:EQA_EXCHANGE_CNSESH -> EQA;EXCHANGE;CNSESH
深市A股:EQA_EXCHANGE_CNSESZ -> EQA;EXCHANGE;CNSESZ

fiddle: %2C is ,
http://quotes.money.163.com/hs/service/diyrank.php?page=0&query=STYPE%3AEQA&fields=NO%2CSYMBOL%2CNAME%2CPRICE%2CPERCENT%2CUPDOWN%2CFIVE_MINUTE%2COPEN%2CYESTCLOSE%2CHIGH%2CLOW%2CVOLUME%2CTURNOVER%2CHS%2CLB%2CWB%2CZF%2CPE%2CMCAP%2CTCAP%2CMFSUM%2CMFRATIO.MFRATIO2%2CMFRATIO.MFRATIO10%2CSNAME%2CCODE%2CANNOUNMT%2CUVSNEWS&sort=PERCENT&order=desc&count=24&type=query HTTP/1.1
simple:
http://quotes.money.163.com/hs/service/diyrank.php?page=0&query=STYPE%3AEQA%3BEXCHANGE%3ACNSESH&fields=NO,SYMBOL,NAME,PRICE,YESTCLOSE,OPEN,FIVE_MINUTE&sort=NO&order=desc&count=24&type=query
http://quotes.money.163.com/hs/service/diyrank.php?page=0&query=STYPE:EQA;EXCHANGE;CNSESH&fields=NO,SYMBOL,NAME,PRICE,YESTCLOSE,OPEN,FIVE_MINUTE&sort=SYMBOL&order=asc&count=24&type=query

sort=SYMBOL

163
日内实时盘口（JSON）：
http://api.money.126.net/data/feed/1000002,1000001,1000881,0601398,money.api

历史成交数据（CSV）：
http://quotes.money.163.com/service/chddata.html?code=0601398&start=20000720&end=20150508

财务指标（CSV）：
http://quotes.money.163.com/service/zycwzb_601398.html?type=report

资产负债表（CSV）：
http://quotes.money.163.com/service/zcfzb_601398.html

利润表（CSV）：
http://quotes.money.163.com/service/lrb_601398.html

现金流表（CSV）：
http://quotes.money.163.com/service/xjllb_601398.html

杜邦分析（HTML）：
http://quotes.money.163.com/f10/dbfx_601398.html
"""

class ReferenceSpider(BasicSpider):


    def __init__(self):
        super(ReferenceSpider, self).__init__("Reference Spider")
        self.page = 0
        self.query_section = "STYPE:EQA;EXCHANGE;CNSESH"
        self.count = 1000
        self.fields = ['NO','SYMBOL','NAME','PRICE','OPEN','YESTCLOSE']
        self.BASE_URL = "http://quotes.money.163.com/hs/service/diyrank.php"

        self.decoder = json.JSONDecoder()

    def get_page_url(self, page):
        self.request_url = "%s?page=%d&query=%s&count=%d&type=query&sort=SYMBOL&order=asc&fields=%s" % (
            self.BASE_URL,
            self.page,
            self.query_section,
            self.count,
            ','.join(self.fields)
        )

    def run(self):
        self.total_item = 0
        self.max_page = 50

        # batch process
        docs = []
        while self.page < self.max_page:
            logger.info("requesting:%d" % self.page)
            self.get_page_url(self.page)
            req = urllib2.Request(url=self.request_url, headers=spider.utils.get_default_header())
            res = urllib2.urlopen(req)
            dt = spider.unzip_stream(res.read())
            jo = self.decoder.decode(dt)
            total = jo['total']
            self.max_page = jo['pagecount']
            for item in jo['list']:
                self.total_item += 1
                #print "%s-%s" % (item['SYMBOL'], item["NAME"])
                docs.append((item['SYMBOL'], item["NAME"]))
            self.page += 1

        logger.info("total:%d" % self.total_item)

        self.process(docs)
