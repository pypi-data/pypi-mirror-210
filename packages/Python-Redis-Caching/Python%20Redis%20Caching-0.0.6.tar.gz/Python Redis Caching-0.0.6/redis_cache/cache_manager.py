import redis
import json
from datetime import timedelta

from typing import Callable

class CacheManager:

    def __init__(self, host, port=6379, db=1, expiration=timedelta(days=1)) -> None:
        self._redis_cli = redis.Redis(host=host, port=port, decode_responses=True, db=db)
        self._expiration = expiration
    
    def _save_to_cache(self, key: str, data: dict) -> None:
        self._redis_cli.set(key, json.dumps(data), ex=self._expiration)

    def _get_from_cache(self, key: str) -> dict | None:
        if not self._redis_cli.exists(key):
            return None
        return json.loads(self._redis_cli.get(key))

    def use_cache(self, key: str, f: Callable, *args, **kwargs):
        full_key = f'{key}_{hash(args)}'
        cache_data = self._get_from_cache(full_key)
        if cache_data is not None:
            return cache_data
        result = f(*args, **kwargs)
        self._save_to_cache(full_key, result)
        return result
