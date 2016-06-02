# coding:utf-8

__all__ = ['Document']

class Document(object):

    def __init__(self):
        self.doc = {
            'Id': '',
            'title': '',
            'body': '',
            'post_time': '',

            'author': '',
            'authorId': '',

            'ref_link': ''
        }
