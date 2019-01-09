import toml
import os
from pathlib import Path
from log import logger
from collections import namedtuple

BASE_DIR = Path(__file__).parent


class Config:
    pass


class DatabaseConfig(Config):
    _params = {}

    def __init__(self, scheme: str, host: str, port: int, database_name: str, username: str, password: str):
        self._scheme = scheme
        self.host = host
        self.port = port
        self.database_name = database_name
        self.username = username
        self._password = password

    @property
    def password(self):
        return self._password

    @property
    def params(self):
        return '&'.join(['='.join(_) for _ in self._params.items()])

    @property
    def uri(self):
        return f'{self._scheme}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}?{self.params}'


class MssqlDatabaseConfig(DatabaseConfig):
    _params = {
        'driver': 'ODBC Driver 17 for SQL Server'
    }

    def __init__(self, **kwargs):
        super().__init__(scheme='mssql+pyodbc', **kwargs)


class OracleDatabaseConfig(DatabaseConfig):

    def __init__(self, ld_library_path, nls_lang, **kwargs):
        if nls_lang:
            os.environ['NLS_LANG'] = nls_lang

        if ld_library_path:
            os.environ['LD_LIBRARY_PATH'] = ld_library_path

        super().__init__(scheme='oracle+cx_oracle', **kwargs)


class QueueConfig(Config):
    def __init__(self, name, message_type):
        self.name = name
        self.message_type = message_type


class MssqlQueueConfig(QueueConfig):
    def __init__(self, service, contract, **kwargs):
        self.service = service
        self.contract = contract
        super().__init__(**kwargs)


class OracleQueueConfig(QueueConfig):
    pass


LogConfig = namedtuple('LogConfig', ['debug', 'file_name'])

SyncConfig = namedtuple('SyncConfig', ['departments_table', 'users_table', 'relationships_table'])

JdyApiConfig = namedtuple('JdyApiConfig', ['api_key', 'safe_limit'])

WeChatConfig = namedtuple('WeChatConfig', ['corp_id', 'agent_id', 'agent_secret', 'party_id'])


def init_config():
    try:
        config = toml.load(Path.joinpath(BASE_DIR, 'config.toml'))
    except TypeError as e:
        logger.critical(f'加载配置文件错误 - {e}')
        raise e
    except FileNotFoundError as e:
        logger.critical(f'找不到指定的配置文件 - {e}')
        raise e
    except toml.TomlDecodeError as e:
        logger.critical(f'配置文件解析错误 - {e}')
        raise e
    return config


def build_database_config(config: dict, driver: str) -> DatabaseConfig:
    _configs = {
        'oracle': OracleDatabaseConfig,
        'mssql': MssqlDatabaseConfig
    }
    _config = _configs[driver](**config['database'][driver])

    return _config


def build_queue_config(config: dict, driver) -> QueueConfig:
    _configs = {
        'oracle': OracleQueueConfig,
        'mssql': MssqlQueueConfig
    }
    _config = _configs[driver](**config['queue'][driver])
    return _config


try:
    configs = init_config()
    db_driver = configs['db_driver'].lower()
    config_title = configs['title']
    jdy_config = JdyApiConfig(**configs['jian_dao_yun'])
    wechat_config = WeChatConfig(**configs['wechat'])
    database_config = build_database_config(configs, db_driver)
    queue_config = build_queue_config(configs, db_driver)
    log_config = LogConfig(**configs['log'])
    sync_config = SyncConfig(**configs['sync'])
except Exception as error:
    logger.error(f'请检查配置文件：{error}', exc_info=False)
    raise error
