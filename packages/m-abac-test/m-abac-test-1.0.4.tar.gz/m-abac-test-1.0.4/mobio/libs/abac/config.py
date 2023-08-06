import os
import redis

from mobio.libs.Singleton import Singleton
from mobio.libs.caching import LruCache


class StoreCacheType:
    LOCAL = 1
    REDIS = 2


class Cache:
    REDIS_URI = "{}?health_check_interval=30".format(os.environ.get("ADMIN_REDIS_URI", os.environ.get("REDIS_URI")))
    PREFIX = "m_abac"


lru_cache_redis = LruCache(
    store_type=StoreCacheType.REDIS,
    redis_uri=Cache.REDIS_URI,
    cache_prefix=Cache.PREFIX,
)


class Mobio:
    ADMIN_HOST = os.environ.get("ADMIN_HOST")
    MOBIO_TOKEN = "Basic {}".format(os.environ.get('YEK_REWOP', ''))


@Singleton
class RedisClient(object):

    def __init__(self):
        self.redis_connect = redis.from_url(Cache.REDIS_URI)

    def get_connect(self):
        return self.redis_connect

    def get_value(self, key_cache):
        redis_conn = self.get_connect()
        return redis_conn.get(key_cache)

    def set_value_expire(self, key_cache, value_cache, time_seconds=3600):
        redis_conn = self.get_connect()
        redis_conn.setex(key_cache, time_seconds, value_cache)

    def delete_key(self, key_cache):
        redis_conn = self.get_connect()
        redis_conn.delete(key_cache)

    class KeyCache:
        MERCHANT_USE_ABAC = "merchant_use_abac"
