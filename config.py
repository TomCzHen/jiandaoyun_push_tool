import toml
from pathlib import Path
from log import logger

BASE_DIR = Path(__file__).parent


def build_config(name: str) -> dict:
    try:
        configs = toml.load(Path.joinpath(BASE_DIR, 'config.toml'))
        config = configs[name]
    except TypeError as e:
        logger.critical(f'加载配置文件错误 - {e}')
        raise e
    except FileNotFoundError as e:
        logger.critical(f'找不到指定的配置文件 - {e}')
        raise e
    except toml.TomlDecodeError as e:
        logger.critical(f'配置文件解析错误 - {e}')
        raise e
    except KeyError as e:
        logger.critical(f'找不到配置项 - {e}')
        raise e
    else:
        return config


try:
    db_driver = build_config('db_driver')
    config_title = build_config('title')
    api_config = build_config('jian_dao_yun')
    database_config = build_config('database')
    queue_config = build_config('queue')
    log_config = build_config('log')
    sync_config = build_config('sync')
except Exception as error:
    logger.error('请检查配置文件', exc_info=True)
    raise error
