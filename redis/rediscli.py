# coding:utf-8

from celery import Celery

app = Celery('celery', broker="redis://10.35.16.120:6379/0")

@app.task
def task():
    print 'task is running'


if __name__ == '__main__':
    print 'working'
    cli = RedisCli