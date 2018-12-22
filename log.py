import logging
from logging.handlers import TimedRotatingFileHandler

LOG_FILE_NAME = 'jiandaoyun_push_tool.log'
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(message)s')

console_handler = logging.StreamHandler()

file_handler = TimedRotatingFileHandler(filename=LOG_FILE_NAME, when='midnight', interval=1, backupCount=5)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
