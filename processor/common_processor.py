# coding:utf-8
from db.es import ESWrapper
import re
import pytz
import datetime
from pykafka import KafkaClient
import logging
from logging import StreamHandler
from json import JSONEncoder


class XueQiuProcessor(object):
    """
    convert dict to another dict for ES document
    """
    def __init__(self):
        self.init_kafka()

        self.db_init = False
        self.instrument = 'SHTESTSYM'
        self.last_doc_id = 0

    def init_kafka(self):
        stream_handler = StreamHandler()
        logger = logging.getLogger('pykafka.cluster')
        logger.addHandler(stream_handler)
        logging.getLogger('kazoo.client').addHandler(stream_handler)

        # enabled kafka
        self.kafka_client = KafkaClient(hosts='10.35.22.70:9092')
        print self.kafka_client.topics
        topic = self.kafka_client.topics['social']
        self.producer = topic.get_sync_producer()

    def init_db_connection(self):
        self.db_client = ESWrapper()
        self.db_init = True

    def init_instrument(self, code):
        self.instrument = code
        self.last_doc_id = self.db_client.get_last_id(self.instrument)

    def extract_instrument_list(self, text):
        name_list = []
        code_list = []
        # regex must has one char, avoid $$$, typo
        # TODO: test more cases later
        instrument_list = re.findall('\$(.+?)\$', text)
        if instrument_list:
            for instrument in instrument_list:
                m = re.search('(.*?)\((.*?)\)', instrument)
                if m:
                    instrument_name = m.group(1)
                    instrument_code = m.group(2)
                    name_list.append(instrument_name)
                    code_list.append(instrument_code)
        return name_list, code_list

    def extract_related_user(self, html_text):
        user_list = []
        user_list_1 = re.findall('>@.*?</a>', html_text)
        user_list_2 = re.findall(u'>＠.*?</a>', html_text)
        if user_list_1:
            for user in user_list_1:
                user_list.append(user[2:-4])
        if user_list_2:
            for user in user_list_2:
                user_list.append(user[2:-4])
        return user_list


    def process(self, doc):
        doc['id'] = doc['raw']['id']  # integer type

        if doc['id'] <= self.last_doc_id:
            return True # processed is done = True

        text = doc['raw']['text']
        # enrich document
        doc['enrich'] = {}
        doc['enrich']['instrument'] = {}
        doc['enrich']['instrument']['code'] = self.instrument

        doc['enrich']['author'] = {}
        doc['enrich']['author']['id'] = doc['raw']['user_id']
        doc['enrich']['author']['screen_name'] = doc['raw']['user']['screen_name']

        doc['enrich']['user_list'] = self.extract_related_user(text)
        plain_text = re.sub('<.*?>', '', text)
        plain_text = re.sub('\s*', '', plain_text)
        plain_text = re.sub('(&nbsp;)+', ' ', plain_text)
        name_list, code_list = self.extract_instrument_list(plain_text)
        doc['enrich']['name_list'] = name_list
        doc['enrich']['code_list'] = code_list

        doc['enrich']['plain_text'] = plain_text

        create_at = doc['raw']['created_at']/1000
        create_at_tm_utc = datetime.datetime.fromtimestamp(create_at, pytz.utc)
        create_at_tm_local = datetime.datetime.fromtimestamp(create_at, pytz.timezone('Etc/GMT-8'))
        doc['enrich']['post_time'] = doc['raw']['created_at']
        doc['enrich']['post_time_str'] = create_at_tm_utc.strftime('%Y-%m-%d %H:%M:%S')
        doc['enrich']['post_time_local_str'] = create_at_tm_local.strftime('%Y-%m-%d %H:%M:%S')

        if self.db_init:
            self.db_client.insert(doc)

        #pipeline, kafka introduced
        self.producer.produce(JSONEncoder().encode(doc))
