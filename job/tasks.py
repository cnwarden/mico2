# -*- coding: utf-8 -*-

from rq.decorators import job


def crawl(*args, **kwargs):
    print args
    print kwargs
    print 'crawling....'
    import time
    time.sleep(10)


def HB(*args, **kwargs):
    print kwargs