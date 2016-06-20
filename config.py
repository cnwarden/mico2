import pytz

LOCAL_TIMEZONE = pytz.timezone('Etc/GMT-8')

"""
ELASTIC SEARCH CONFIGURATION
"""
ES_HOST='10.35.22.80:9200'
ES_INDEX='std_content'
ES_INDEX_ALIAS='news'
ES_DOC_TYPE="xueqiu"

"""
DISTRIBUTION TASK QUEUE REDIS CONFIGURATION
"""
REDIS_URL="redis://10.35.19.238:6379/0"


"""
WEB CONSOLE TO MONITOR STATUS
"""
WEB_CONSOLE_HOST='10.35.16.120:8889'


"""
INIT MONITOR STOCKLIST FOR XUEQIU
"""
STOCK_LIST = ['SH000001', 'SZ399001', 'SZ399006', 'DJI30', 'HKHSI', 'SH000016', 'SZ399101']


SPIDER = [
    {
        'name': 'spider-a',
        'class': 'spider.east_spider.EastSpider',
        'enabled': False,
        'pipelines': [
                        'pipeline.SimplePipeline',
                        'pipeline.ESPipeline',
                        'pipeline.StorePipeline'
                    ]
    },

    {
        'name': 'spider-b',
        'class': 'spider.reference_spider.ReferenceSpider',
        'enabled': True,
        'pipelines': [
                        'pipeline.SaveToDictPipeline'
                    ]
    }
]
