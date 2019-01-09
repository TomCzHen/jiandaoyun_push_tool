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
        message = self.__cache.get(f'{self._queue.name}')
        if not message:
            message = self._queue.dequeue_message()
            self.__cache.set(f'{self._queue.name}', message)
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
                logger.info(f'推送失败：{message}')
                self._handle_exception(error, message)
            else:
                self.__cache.delete(f'{self._queue.name}')
                logger.info(f'推送成功：{message}')

    def _handle_exception(self, error, message):
        try:
            raise error
        except InvalidPayload:
            logger.warning('无效的消息 Payload。')
            self.__cache.delete(f'{self._queue.name}')
        except SafeDataLimitException as e:
            logger.warning('匹配表单数据超出安全限制。')
            self.__cache.delete(f'{self._queue.name}')
        except QueueException as e:
            logger.warning('获取队列消息发送错误，3 秒后重试。')
            sleep(3)
        except NetworkError as e:
            logger.warning('请求 API 发生连接错误，1 秒后重试。')
        except APIException as e:
            logger.warning('请求 API 返回错误信息,1 秒后重试。')
            sleep(1)
        except HTTPError as e:
            logger.warning('请求 API 返回 HTTP 错误，1 秒后重试。')
            logger.error(e, exc_info=True)
            sleep(1)
        except Exception as e:
            raise e
