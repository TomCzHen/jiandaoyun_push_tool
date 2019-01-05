from api import JianDaoYun
from time import sleep
from log import logger
from database_queue import Queue, QueueMessage
from handlers import QueueMessageHandler
from cache import queue_cache as cache
from handlers.exceptions import InvalidPayload, HandlerException


class Consumer:
    def __init__(self, queue: Queue, api: JianDaoYun):
        self._queue = queue
        self._api = api
        self._handler = QueueMessageHandler(self._api)

    def _get_message(self) -> QueueMessage:
        message = cache.get('message')
        if not message:
            message = self._queue.dequeue_message()
            cache.set('message', message)
        return message

    def start(self):
        logger.info('Starting Queue Consumer...')
        while True:
            try:
                message = self._get_message()
                if message:
                    logger.debug(f'Message Payload : {message}')
                    self._handler.handle(message)
                else:
                    sleep(3)
            except InvalidPayload as e:
                cache.delete('message')
                logger.warning(e.msg)
            except HandlerException as e:
                cache.delete('message')
                logger.warning(e.msg)
            else:
                cache.delete('message')
