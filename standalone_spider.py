# coding:utf-8


import click

@click.command()
@click.option('--symbol', default='SH000001', help='crawl symbol')
def start_spider(symbol):
    print 'start spider:' + symbol


if __name__ == '__main__':
    start_spider()