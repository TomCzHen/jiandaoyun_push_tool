from api import JianDaoYun, APIException, NetworkError, HTTPError
from time import sleep
from log import logger
from database_queue import Queue, QueueMessage, QueueException
from handlers import QueueMessageHandler
from cache import queue_cache as cache
from handlers.exceptions import InvalidPayload, SafeDataLimitException


class Consumer:
    def __init__(self, queue: Queue, api: JianDaoYun):
        self._queue = queue
        self._api = api
        self._handler = QueueMessageHandler(self._api)
        self.__cache = cache

    def _get_message(self) -> QueueMessage:
        message = self.__cache.get('message')
        if not message:
            message = self._queue.dequeue_message()
            self.__cache.set('message', message)
        return message

    def start(self):
        logger.info('Starting Queue Consumer...')
        while True:
            message = None
            try:
                message = self._get_message()
                if message:
                    logger.debug(f'Message Payload : {message}')
                    self._handler.handle(message)
                else:
                    sleep(3)
            except Exception as error:
                self._handle_exception(error, message)
            else:
                self.__cache.delete('message')

    def _handle_exception(self, error, message):
        try:
            raise error
        except InvalidPayload:
            err_msg = '无效的消息 Payload'
            logger.warning(err_msg)
            self.__cache.delete('message')
        except SafeDataLimitException as e:
            err_msg = '已存在表单数据超出安全限制'
            logger.warning(err_msg)
            self.__cache.delete('message')
        except (QueueException, NetworkError) as e:
            logger.warning(e, exc_info=True)
            sleep(3)
        except APIException as e:
            err_msg = '请求 API 返回错误信息'
            logger.warning(err_msg)
            logger.error(e, exc_info=True)
            sleep(1)
        except HTTPError as e:
            err_msg = '请求 API 返回 HTTP 错误'
            logger.warning(err_msg)
            logger.error(e, exc_info=True)
            sleep(1)
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e
