
import logging
from logging import Formatter, StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler
import os

__all__ = ['logger', 'debug_logger', 'master_logger', 'worker_logger', 'operation_logger']


if not os.path.exists("log/"):
    os.mkdir("log/")

logger = logging.getLogger('mico2')
logger.setLevel(logging.DEBUG)

FORMAT = '[%(asctime)-15s]%(message)s'
formatter = Formatter(fmt=FORMAT)
rotate_handler = RotatingFileHandler('log/mico.log', maxBytes=1*1024*1024, backupCount=10, encoding='utf-8')
rotate_handler.setFormatter(formatter)
stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(rotate_handler)
logger.addHandler(stream_handler)

debug_logger = logging.getLogger('debuger')
debug_logger.setLevel(logging.DEBUG)
fh_handler = FileHandler('log/debug.log', 'w', encoding='utf-8')
fh_handler.setFormatter(formatter)
debug_logger.addHandler(fh_handler)

master_logger = logging.getLogger('master')
master_logger.setLevel(logging.DEBUG)
fh_handler = FileHandler('log/master.log', 'w', encoding='utf-8')
fh_handler.setFormatter(formatter)
master_logger.addHandler(fh_handler)

worker_logger = logging.getLogger('worker')
worker_logger.setLevel(logging.DEBUG)
fh_handler = FileHandler('log/worker.log', 'w', encoding='utf-8')
fh_handler.setFormatter(formatter)
worker_logger.addHandler(fh_handler)

operation_logger = logging.getLogger('operation')
operation_logger.setLevel(logging.DEBUG)
fh_handler = FileHandler('log/operation.log', 'w', encoding='utf-8')
fh_handler.setFormatter(formatter)
operation_logger.addHandler(fh_handler)
