# Use Redis as a backend for caching

```python
from redis_cache.cache_manager import CacheManager
from datetime import timedelta
from time import sleep

cache = CacheManager('localhost', port=6379, db=1, expiration=timedelta(days=1))

def sum(a, b):
    sleep(2)
    return a + b

cache('S', sum, 8, 5) # Took 2.1s
cache('S', sum, 8, 5) # Took 1.8ms
```