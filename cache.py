from diskcache import Cache
from pathlib import Path
from config import BASE_DIR

queue_cache = Cache(Path.joinpath(BASE_DIR, '.cache/queue'))
widgets_cache = Cache(Path.joinpath(BASE_DIR, '.cache/widgets'))
api_cache = Cache(Path.joinpath(BASE_DIR, '.cache/api'))
notice_cache = Cache(Path.joinpath(BASE_DIR, '.cache/notice'))
