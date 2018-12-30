from log import logger
from api import JianDaoYun
from database_queue import Queue, QueueMessage
from handlers import QueueMessageHandler, FormDataHandler
from cache import queue_cache as cache
from handlers.exceptions import InvalidPayload


class Consumer:
    def __init__(self, queue: Queue, api: JianDaoYun):
        self._db_queue = queue
        self._api = api
        self._queue_message_handler = QueueMessageHandler(self._api)
        self._form_data_handler = FormDataHandler(self._api)

    def _get_message(self) -> QueueMessage:
        message = cache.get('message')
        if not message:
            message = self._db_queue.dequeue_message()
            cache.set('message', message)
        return message

    def start(self):
        logger.info('Starting Queue Consumer...')
        while True:
            try:
                message = self._get_message()
                if message:
                    form_data = self._queue_message_handler.create_form_data(message)
                    self._form_data_handler.handle_form_data(form_data)
            except InvalidPayload as e:
                logger.warning(e)
                cache.delete('message')
