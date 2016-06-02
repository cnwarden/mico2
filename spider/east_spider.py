# coding:utf-8

from __future__ import absolute_import
from spider.basic_spider import BasicSpider
from utils.logger import logger
from bs4 import BeautifulSoup
import urllib2
import spider.utils
import document

class EastSpider(BasicSpider):

    def __init__(self):
        super(EastSpider, self).__init__("EastMoney Spider")
        self.BASE_URL = 'http://guba.eastmoney.com'

    def run(self):
        url = 'http://guba.eastmoney.com/list,603993,99.html'
        req = urllib2.Request(url=url, headers=spider.utils.get_default_header())
        res = urllib2.urlopen(req)
        soup = BeautifulSoup(res.read())
        topics = soup.find_all("div", attrs={"class":"articleh"})

        self.subpage = []
        for topic in topics:
            topic_link = topic.find('a')
            link = '%s%s' % (self.BASE_URL, topic_link['href'])
            title = topic_link['title']
            self.subpage.append((title, link))

        for topic_page in self.subpage:
            url = topic_page[1]
            req = urllib2.Request(url=url, headers=spider.utils.get_default_header())
            res = urllib2.urlopen(req)
            soup = BeautifulSoup(res.read())
            e = soup.find('div', attrs={'id': 'zwconttbt'})
            title = e.get_text().strip()
            e = soup.find('div', attrs={'id':'zwconbody'})
            text = e.get_text().strip()
            e = soup.find('div', attrs={'class': 'zwfbtime'})
            ptime = e.get_text().strip()
            #logger.info('%s-%s-%s' % (url, title, text))
            # construct document
            d = document.Document()
            d.doc['title'] = title
            d.doc['body'] = text
            d.doc['post_time'] = ptime
            d.doc['ref_link'] = url
            # process document
            self.process(d)



