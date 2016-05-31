#! coding:utf-8

import sys
from utils.logger import logger
import os
import version

logger.info('mico application start')
logger.info('version:%s' % version.VERSION)
logger.debug('PYTHONPATH:' + os.getenv('PYTHONPATH'))

from getopt import getopt
from rest.web_service import app
from job.manager import Manager
import config

if len(sys.argv) <= 1:
    logger.fatal('missed startup parameters')
    sys.exit(0)

opts, args = getopt(sys.argv[1:], 'icws:t', longopts=['--init', '--console', '--web', '--stock', '--top'])
for o, a in opts:
    if o in ['-i']:
        logger.info('init db index, it will remove old index data, backup if needed')
        from db.es import ESWrapper
        es = ESWrapper()
        es.init_index()
    elif o in ['-c']:
        logger.info('console mode startup')
        Manager.test_job()
    elif o in ['-s']:
        logger.info('get history data')
        insts = a.split(',')
        Manager.run_spider_job(instruments=insts)
    elif o in ['-w']:
        logger.info('web console mode startup')
        Manager.start()
        endpoint = config.WEB_CONSOLE_HOST.split(':')
        logger.info('web endpoint:' + ':'.join(endpoint))
        app.run(host=endpoint[0], port=int(endpoint[1]))
    elif o in ['-t']:
        logger.info('topN extract')
        Manager.run_spider_top_N(10)
    else:
        logger.info('wrong paramters, application exit')
        sys.exit(0)
