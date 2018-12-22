import toml
import argparse
import logging
from time import sleep
from diskcache import Cache
from log import logger
from api import JianDaoYun, WeChatAgent
from formdata import FormData
from database_queue import Queue, QueueMessage, OracleQueue, MssqlQueue

queue_cache = Cache('.cache/queue')
form_data_cache = Cache('.cache/form_data')


class QueueMessageHandler:
    def __init__(self, api: JianDaoYun):
        self._api = api

    def create_form_data(self, message: QueueMessage):
        app_id = message.payload['app_id']
        entry_id = message.payload['entry_id']
        widgets = self._get_from_data_widgets(app_id=app_id, entry_id=entry_id)
        form_data = FormData.create_form_data(widgets=widgets, payload=message.payload)

        return form_data

    def _get_from_data_widgets(self, app_id: str, entry_id: str) -> list:
        widgets = queue_cache.get(f'{app_id}-{entry_id}', None)
        if not widgets:
            widgets = self._api.fetch_form_widgets(app_id=app_id, entry_id=entry_id)
        return widgets


class FormDataHandler:
    def __init__(self, api: JianDaoYun):
        self._api = api

    def handle_form_data(self, form_data: FormData):
        pass


class QueueConsumer:
    def __init__(self, queue: Queue, api: JianDaoYun):
        self._queue = queue
        self._api = api
        self._queue_message_handler = QueueMessageHandler(self._api)
        self._form_data_handler = FormDataHandler(self._api)

    def get_message(self) -> QueueMessage:
        message = queue_cache.get('message')
        if not message:
            message = self._queue.dequeue_message()
            queue_cache.set('message', message)
        return message

    def start(self):
        while True:
            message = self.get_message()
            if message:
                form_data = self._queue_message_handler.create_form_data(message)
                self._form_data_handler.handle_form_data(form_data)


def init_log(config: dict):
    parser = argparse.ArgumentParser(description='Jian Dao Yun Message Consumer')
    parser.add_argument('--debug', help='enable debug mode', action="store_true")
    args = parser.parse_args()
    if args.debug or config.get('debug', False):
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('--- Debug Mode Enable ---')
    else:
        logging.getLogger().setLevel(logging.INFO)


def init_config(name) -> dict:
    try:
        configs = toml.load('config.toml')
        config = configs[name]
    except TypeError as error:
        logger.critical('加载配置文件错误 - {}'.format(error), exc_info=True)
        raise error
    except FileNotFoundError as error:
        logger.critical('找不到指定的配置文件 - {}'.format(error), exc_info=True)
        raise error
    except toml.TomlDecodeError as error:
        logger.critical('配置文件解析错误 - {}'.format(error), exc_info=True)
        raise error
    except KeyError as error:
        logger.critical('找不到配置项 - {}'.format(error), exc_info=True)
    else:
        return config


def init_queue(config: dict) -> Queue:
    _queues = {
        'mssql': MssqlQueue,
        'oracle': OracleQueue
    }
    db_driver: str = config['driver']
    _config = config[db_driver]
    queue = _queues[db_driver.lower()](**_config)
    return queue


def init_api(config: dict) -> JianDaoYun:
    api = JianDaoYun(**config)
    return api


if __name__ == '__main__':
    log_config = init_config('log')
    db_config = init_config('database')
    jdy_config = init_config('jiandaoyun')

    init_log(log_config)

    db_queue = init_queue(db_config)
    jdy_api = init_api(jdy_config)

    queue_consumer = QueueConsumer(queue=db_queue, api=jdy_api)
    queue_consumer.start()
