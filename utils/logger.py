
import logging
from logging import Formatter, StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler

__all__ = ['logger', 'debug_logger']

logger = logging.getLogger('mico2')
logger.setLevel(logging.DEBUG)

FORMAT = '[%(asctime)-15s]%(message)s'
formatter = Formatter(fmt=FORMAT)
rotate_handler = RotatingFileHandler('mico.log', maxBytes=1*1024*1024, backupCount=10, encoding='utf-8')
rotate_handler.setFormatter(formatter)
stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(rotate_handler)
logger.addHandler(stream_handler)


debug_logger = logging.getLogger('debuger')
debug_logger.setLevel(logging.DEBUG)
fh_handler = FileHandler('debug.log', 'w', encoding='utf-8')
fh_handler.setFormatter(formatter)
debug_logger.addHandler(fh_handler)
