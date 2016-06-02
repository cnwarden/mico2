# coding:utf-8

import socket

class MessageType(object):
    MESSAGE_HEARTBEAT = 0
    MESSAGE_JOB       = 1

class BaseMessage(object):

    def get(self):
        return {}

    def timestamp(self):
        import datetime
        import time
        return time.mktime(datetime.datetime.utcnow().timetuple())

    def __str__(self):
        return 'BaseMessage'

class HBMessage(BaseMessage):

    def get(self):
        return {
            'type':         MessageType.MESSAGE_HEARTBEAT,
            'hostname':     socket.gethostname(),
            'timestamp':    super(HBMessage, self).timestamp()
        }