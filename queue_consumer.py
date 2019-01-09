from api import JianDaoYun, APIException, NetworkError, HTTPError
from time import sleep
from log import logger
from database_queue import Queue, QueueMessage, QueueException
from handlers import QueueMessageHandler
from cache import queue_cache as cache
from handlers.exceptions import InvalidPayload, SafeDataLimitException
from notifications.channels import Notification, Channel


class Consumer:
    def __init__(self, queue: Queue, api: JianDaoYun, channel: Channel):
        self._queue = queue
        self._api = api
        self._channel = channel
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
            except QueueException as e:
                logger.warning('获取队列消息发送错误，10 秒后重试。')
                sleep(10)

            if message:
                try:
                    logger.debug(f'Message Payload : {message}')
                    self._handler.handle(message)
                except Exception as error:
                    logger.info(f'推送失败：{message}')
                    self._handle_exception(error, message)
                else:
                    self.__cache.delete(f'{self._queue.name}')
                    logger.info(f'推送成功：{message}')
            else:
                sleep(3)

    def _handle_exception(self, error, message=None):
        err_msg = None
        try:
            raise error
        except InvalidPayload:
            err_msg = '无效的消息 Payload。'
            logger.warning(err_msg)
            self.__cache.delete(f'{self._queue.name}')
        except SafeDataLimitException as e:
            err_msg = '匹配表单数据超出安全限制。'
            logger.warning(err_msg)
            self.__cache.delete(f'{self._queue.name}')
        except NetworkError as e:
            err_msg = '请求 API 发生连接错误，请检查日志。'
            logger.warning(err_msg)
        except APIException as e:
            err_msg = '请求 API 返回错误信息，请检查日志。'
            logger.warning(err_msg)
            sleep(1)
        except HTTPError as e:
            err_msg = '请求 API 返回 HTTP 错误，请检查日志。'
            logger.warning(err_msg)
            logger.error(e, exc_info=True)
            sleep(1)
        except Exception as e:
            raise e
        finally:
            if err_msg:
                notice = Notification(message=f'{err_msg}', payload=message.payload)
                self._channel.send(notice)
