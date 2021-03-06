import logging
from logging.handlers import TimedRotatingFileHandler
from log import logger, formatter
from pathlib import Path
from sqlalchemy import create_engine
from config import BASE_DIR, db_driver, config_title, log_config, database_config, jdy_config, queue_config, \
    sync_config, wechat_config
from api import JianDaoYun
from database_queue import Queue, OracleQueue, MssqlQueue
from queue_consumer import Consumer as QueueConsumer
from handlers import ContactsHandler
from args import args as run_args
from notifications.channels import WeChatChannel


def init_queue(config, engine) -> Queue:
    logger.info('初始化队列')
    _queues = {
        'mssql': MssqlQueue,
        'oracle': OracleQueue
    }
    queue = _queues[db_driver.lower()](engine=engine, config=config)
    return queue


def init_logger(config):
    file_name = config.file_name
    full_file_name = Path.joinpath(BASE_DIR, file_name)
    file_handler = TimedRotatingFileHandler(filename=full_file_name, encoding='utf-8', when='midnight', interval=1,
                                            backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if run_args.debug or config.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logger.info(f'初始化日志')
    logger.info(f'加载配置 >>> {config_title} <<<,数据库类型 >>> {db_driver} <<<')


def init_channel(config):
    channel = WeChatChannel(config)
    return channel


if __name__ == '__main__':
    try:
        init_logger(log_config)
        db_engine = create_engine(database_config.uri)
        db_queue = init_queue(queue_config, db_engine)
        jdy_api = JianDaoYun(jdy_config)
        wechat_channel = init_channel(wechat_config)
    except Exception as e:
        logger.error('初始化错误，请检查配置。', exc_info=True)
        raise e

    try:
        if run_args.daemon:
            queue_consumer = QueueConsumer(queue=db_queue, api=jdy_api, channel=wechat_channel)
            queue_consumer.start()
    except Exception as e:
        logger.error('消费者程序因未知异常退出。')
        raise e

    try:
        if run_args.sync:
            departments_response = jdy_api.fetch_department_list(dept_id='root', has_child=True)
            departments = departments_response.json()['departments']

            users_response = jdy_api.fetch_member_list(dept_id='root', has_child=True)
            users = users_response.json()['users']

            contacts_handler = ContactsHandler(engine=db_engine, config=sync_config)
            contacts_handler.handle(users=users, departments=departments)
    except Exception as e:
        logger.error('同步程序因未知异常退出。', exc_info=True)
        raise e
