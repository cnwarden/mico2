# coding:utf-8

import click
import elasticsearch
import config
import os
import sys
from utils.logger import operation_logger

es = elasticsearch.Elasticsearch(hosts=config.ES_HOST)

@click.group()
def cli():
    pass

@click.command()
def list_index(list):
    if(list):
        operation_logger.info('list_index')
        data = es.cat.indices()
        print data

@click.command()
def create_template():
    operation_logger.info('create_template')
    template = 'data/es_template/content.json'
    if(not os.path.exists(template)):
        print 'template not exists'
        sys.exit(0)

    try:
        with open(template) as fp:
            body = fp.read()
            es.indices.put_template(name="content", body=body)
            print 'created template named content'
    except Exception as ex:
        print ex

@click.command()
@click.option("--limit", default=5, help="document count limitation")
def show_docs(limit):
    operation_logger.info('show_docs')
    body = {
        "size": limit,
        "fields": ['enrich.post_time_local_str', 'enrich.instrument.code'],
        "query": {
            "match_all": {}
        },
        "sort": {
            "enrich.post_time": "desc"
        }
    }
    docs = es.search(index=config.ES_INDEX_ALIAS, doc_type=config.ES_DOC_TYPE, body=body)
    for idx, doc in enumerate(docs['hits']['hits']):
        print '[%05d]%s-%s' % (idx, doc['fields']['enrich.post_time_local_str'], doc['fields']['enrich.instrument.code'])

cli.add_command(list_index)
cli.add_command(create_template)
cli.add_command(show_docs)

if __name__ == '__main__':
    cli()