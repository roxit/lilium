import logging
LOG_FORMAT = '[%(asctime)s] %(name)s: %(levelname)s:%(message)s'
logging.basicConfig(format=LOG_FORMAT, handler=logging.StreamHandler())

from client import Client

