
from elasticsearch import Elasticsearch
from utils.logger import logger
from config import *
from json import JSONEncoder
import codecs
import operator
import datetime
import pytz

class ESWrapper(object):

    def __init__(self):
        host = ES_HOST
        logger.info('connecting to es db:%s' % (host))
        self.client = Elasticsearch(hosts=host)

    def init_index(self):
        self.client.indices.delete(ES_INDEX_ALIAS, ignore=[404])
        self.client.indices.create(ES_INDEX, body=
        {
            'settings':{
                'number_of_shards': 1,
                'number_of_replicas': 1,
            },
            'aliases': {
                ES_INDEX_ALIAS:{}
            },
            "mappings": {
                ES_DOC_TYPE:{
                    "dynamic_templates":[{
                        "strings":{
                            "match_mapping_type":"string",
                            'mapping':{
                                'type':'string',
                                'index':'no'
                            }
                        }
                    }],
                    "properties": {
                        'enrich': {
                            'properties': {
                                'instrument': {
                                    'properties': {
                                        'code': {
                                            'type': 'string',
                                            'index': 'not_analyzed'
                                        }
                                    }
                                },
                                'name_list': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                },
                                'code_list': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                },
                                'user_list': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                },
                                'plain_text': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                },
                                'auother': {
                                    'properties': {
                                        'id': {
                                            'type': 'long'
                                        },
                                        'screen_name': {
                                            'type': 'string',
                                            'index': 'not_analyzed'
                                        }
                                    }
                                },
                                'post_time': {
                                    'type': 'date',
                                    'format': 'epoch_millis'
                                },
                                'post_time_str': {
                                    'type': 'date',
                                    'format': 'yyyy-MM-dd HH:mm:ss'
                                },
                                'post_time_local_str': {
                                    'type': 'date',
                                    'format': 'yyyy-MM-dd HH:mm:ss'
                                }
                            }
                        }
                    }
                }
            }
        })
        logger.info('index is initalized')

    def insert(self, body):
        # ignore document if existed
        # 409 exist?
        self.client.create(ES_INDEX_ALIAS, ES_DOC_TYPE, body, id=str(body['raw']['id']), ignore=[404, 400, 409])

    def get_last_id(self, instrument):
        last_doc = 0
        try:
            doc = self.client.search(index=ES_INDEX_ALIAS, doc_type=ES_DOC_TYPE, body=
            {
                "size":1,
                "query":{
                    "term": {
                        "enrich.instrument.code":{
                            "value" : instrument
                        }
                    }
                },
                "sort":[
                    {
                        "raw.id":{"order":"desc"}
                    }
                ]
            })
            if doc and doc.has_key('hits') and doc['hits']['total'] > 0:
                last_doc = doc['hits']['hits'][0]['sort'][0]
        except Exception, ex:
            logger.fatal('search error:')
            logger.fatal(ex)
        logger.info('instrument:%s, last doc id:%d' % (instrument, last_doc))
        return last_doc

    def get_doc_list(self, sym=None, count=20):
        last_doc = None
        search_body = {
            "fields": [
               "enrich.instrument.code",
               "enrich.id",
               "enrich.plain_text",
                'enrich.post_time_local_str'
            ],
            'sort':[
                {
                    'raw.id': {'order':'desc'}
                }
            ]
        }
        if sym:
            search_body['query'] = { 'term': { 'enrich.instrument.code': sym } }
        else:
            search_body['query'] = { 'match_all': {} }

        doc = self.client.search(index=ES_INDEX_ALIAS, doc_type=ES_DOC_TYPE, body=search_body, size=count)
        if doc and doc.has_key('hits') and doc['hits']['total'] > 0:
            last_doc = doc['hits']['hits']

        return last_doc

    def dump(self):
        import datetime
        dstr = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = 'dump_%s.json' % (dstr)
        fp = codecs.open(dump_file, mode='w', encoding='utf-8')
        pos = self.client.search(index=ES_INDEX_ALIAS, doc_type=ES_DOC_TYPE,
                                 search_type = 'scan',
                                 scroll='2m',
                                 size=1000,
                                 body={
                                     'query':{
                                         'match_all': {}
                                     }
                                 })
        sid = pos['_scroll_id']
        scroll_size = pos['hits']['total']
        total_size = 0
        while (scroll_size > 0):
            logger.info('scrolling...')
            page = self.client.scroll(scroll_id = sid, scroll = '2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            scroll_size = len(page['hits']['hits'])
            total_size += scroll_size
            logger.info("scroll size: " + str(scroll_size))
            for doc in page['hits']['hits']:
                fp.write(JSONEncoder().encode(doc['_source']['raw']))
                fp.write('\n')
        fp.close()
        return dump_file, total_size

    def get_stats(self, inst):
        count = 0
        search_body = {
                         'query':{
                            'term':{
                                 'enrich.code_list':{
                                    'value': inst
                                 }
                             }
                         }
                     }

        search_body['filter'] = self.__get_filter_query()

        doc = self.client.search(index=ES_INDEX_ALIAS,
                                 doc_type=ES_DOC_TYPE,
                                 size=0,
                                 body=search_body)
        if doc and doc.has_key('hits'):
            count = doc['hits']['total']
        return count

    def get_rank(self):
        stats = {}
        for stock in STOCK_LIST:
            stats[stock] = self.get_stats(stock)

        sorted_stock = sorted(stats.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_stock

    def __get_midnight(self):
        now = datetime.datetime.now(pytz.timezone('Etc/GMT-8'))
        df = '%04d-%02d-%02d %02d:%02d:%02d' % (now.year, now.month, now.day, 0, 0, 0)
        return df

    def __get_now(self):
        now = datetime.datetime.now(pytz.timezone('Etc/GMT-8'))
        dt = now.strftime('%Y-%m-%d %H:%M:%S')

    def __get_filter_query(self):
        return {
            'range':{
                    'enrich.post_time_local_str':{
                        'from': self.__get_midnight(),
                        'to': self.__get_now()
                    }
                }
            }

    def get_all_ranks(self):
        user_dict = {}
        code_dict = {}
        name_dict = {}

        search_body = {
                         'query':{
                             'match_all': {}
                         }
                     }
        filterByTime = True
        if filterByTime:
            search_body['filter'] = self.__get_filter_query()

        pos = self.client.search(index=ES_INDEX_ALIAS, doc_type=ES_DOC_TYPE,
                                 search_type = 'scan',
                                 scroll='2m',
                                 size=1000,
                                 body=search_body)
        sid = pos['_scroll_id']
        scroll_size = pos['hits']['total']
        total_size = 0
        while (scroll_size > 0):
            logger.info('scrolling...')
            page = self.client.scroll(scroll_id = sid, scroll = '2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            scroll_size = len(page['hits']['hits'])
            total_size += scroll_size
            logger.info("scroll size: " + str(scroll_size))
            for doc in page['hits']['hits']:
                users = doc['_source']['enrich']['user_list']
                codes = doc['_source']['enrich']['code_list']
                names = doc['_source']['enrich']['name_list']
                for user in users:
                    if user_dict.has_key(user):
                        user_dict[user] +=1
                    else:
                        user_dict[user] = 1
                for code in codes:
                    if code_dict.has_key(code):
                        code_dict[code] +=1
                    else:
                        code_dict[code] = 1
                for name in names:
                    if name_dict.has_key(name):
                        name_dict[name] +=1
                    else:
                        name_dict[name] = 1

        sorted_user = sorted(user_dict.items(), key=operator.itemgetter(1), reverse=True)
        sorted_code = sorted(code_dict.items(), key=operator.itemgetter(1), reverse=True)
        sorted_name = sorted(name_dict.items(), key=operator.itemgetter(1), reverse=True)
        summary = {
            'total_docs': total_size,
            'total_users': len(sorted_user),
            'total_codes': len(sorted_code)
        }

        return {
            'summary': summary,
            'user_rank': sorted_user,
            'code_rank': sorted_code,
            'name_rank': sorted_name
        }


