import logging
import os
from logging.handlers import TimedRotatingFileHandler
from time import sleep
from log import logger
from pathlib import Path
from sqlalchemy import create_engine
from config import BASE_DIR, db_driver, config_title, log_config, database_config, api_config, queue_config
from api import JianDaoYun, WeChatAgent
from database_queue import Queue, OracleQueue, MssqlQueue
from queue_consumer import Consumer as QueueConsumer
from args import args as run_args


def init_contacts_sync(config: dict):
    pass


def init_db_engine(config: dict):
    logger.debug(f'数据库配置 : {config}')
    logger.info('初始化数据库连接')
    uri_formats = {
        'oracle': 'oracle+cx_oracle://{username}:{password}@{host}:{port}/{database_name}',
        'mssql': 'mssql+pyodbc://{username}:{password}@{host}:{port}/{database_name}?driver=ODBC Driver 17 for SQL Server'
    }

    _config: dict = config[db_driver]

    if db_driver.lower() == 'oracle':
        os.environ['NLS_LANG'] = _config.get('nls_lang')
        os.environ['LD_LIBRARY_PATH'] = _config.get('ld_library_path')

    uri = uri_formats[db_driver.lower()].format(**_config)
    engine = create_engine(uri)
    return engine


def init_queue(config: dict, engine) -> Queue:
    logger.debug(f'队列配置 : {config}')
    logger.info('初始化队列')
    _queues = {
        'mssql': MssqlQueue,
        'oracle': OracleQueue
    }
    _config = config[db_driver]
    queue = _queues[db_driver.lower()](engine=engine, **_config)
    return queue


def init_api(config: dict) -> JianDaoYun:
    logger.debug(f'简道云 API 配置 : {config}')
    logger.info('初始化简道云 API')
    api = JianDaoYun(**config)
    return api


def init_logger(config: dict):
    file_name = config.get('file_name', 'jiandaoyun_push_tool.log')
    full_file_name = Path.joinpath(BASE_DIR, file_name)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler = TimedRotatingFileHandler(filename=full_file_name, when='midnight', interval=1, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if run_args.debug or config.get('debug', False):
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('--- Debug Mode Enable ---')
    else:
        logging.getLogger().setLevel(logging.INFO)

    logger.info(f'初始化日志')
    logger.info(f'加载配置 >>> {config_title} <<<')
    logger.info(f'数据库类型 >>> {db_driver} <<<')


if __name__ == '__main__':
    try:
        init_logger(log_config)
        db_engine = init_db_engine(database_config)
        db_queue = init_queue(queue_config, db_engine)
        jdy_api = init_api(api_config)
    except Exception as e:
        logger.error('初始化错误，请检查配置。', exc_info=True)
        raise e

    try:
        if run_args.daemon:
            queue_consumer = QueueConsumer(queue=db_queue, api=jdy_api)
            queue_consumer.start()
    except Exception as e:
        logger.error('消费者程序因未知异常退出。', exc_info=True)
        raise e

    try:
        if run_args.sync:
            pass
    except Exception as e:
        logger.error('同步程序因未知异常退出。', exc_info=True)
        raise e
