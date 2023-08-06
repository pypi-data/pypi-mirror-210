import logging
from abc import abstractmethod, ABCMeta
from typing import List, Dict
import redis

logger = logging.getLogger("adt_cache")


class AdtCache(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def intersect(self, key: str, vals: List):
        pass

    @abstractmethod
    def differential(self, key: str, vals: List):
        pass

    @abstractmethod
    def push_values(self, key: str, vals: List):
        pass

    @abstractmethod
    def keys(self):
        pass

    @abstractmethod
    def hget(self, hash_name: str) -> Dict:
        """
        hash_name 에 저장된 dict 를 가져온다.
        :param hash_name:
        :return:
        """
        pass

    @abstractmethod
    def hset(self, hash_name: str, dict: Dict[str, any]):
        """
        hash_name 에 dict 를 저장한다.
        :param hash_name:
        :param dict:
        :return:
        """
        pass

    @abstractmethod
    def get(self, key: str) -> str:
        """
        key 에 저장된 값을 가져온다.
        :param key:
        :return:
        """
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        """
        key 에 value 를 저장한다.
        :param key:
        :param value:
        :return:
        """
        pass

class RedisCache(AdtCache):
    def __init__(self, host: str, port: int, db: int, expire_mins: int=60*24, clear_cache=False, decode_res=True):
        logger.info(f"init redis cache with {host}:{port}:{db}")
        super().__init__()
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=decode_res)
        self.expire_mins=expire_mins
        if clear_cache:
            self.redis.flushdb()

    def intersect(self, key, vals: List):
        return [val for val in vals if self.redis.sismember(key, val)]

    def differential(self, key, vals: List):
        return [val for val in vals if not self.redis.sismember(key, val)]

    def push_values(self, key, vals: List):
        self.redis.expire(key, 60 * self.expire_mins)
        return self.redis.sadd(key, *set(vals))

    def keys(self):
        return self.redis.keys()

    def hget(self, hash_name: str) -> Dict:
        return self.redis.hgetall(hash_name)

    def hset(self, hash_name: str, dict: Dict[str, any]):
        for items in dict.items():
            self.redis.hset(hash_name, items[0], items[1])
        self.redis.expire(hash_name, 60 * self.expire_mins)

    def get(self, key: str) -> str:
        return self.redis.get(key)

    def set(self, key: str, value: str):
        self.redis.set(key, value)
        self.redis.expire(key, 60 * self.expire_mins)


class MemoryCache(AdtCache):
    def __init__(self):
        super().__init__()
        self.cache = {}

    def intersect(self, key, vals: List):
        return [val for val in vals if val in self.cache.get(key, [])]

    def differential(self, key, vals: List):
        return [val for val in vals if val not in self.cache.get(key, [])]

    def push_values(self, key, vals: List):
        c = self.cache.get(key)
        if c is None:
            self.cache[key] = set(vals)
        else:
            c.update(vals)

    def keys(self):
        return self.cache.keys()

    def hget(self, hash_name: str) -> Dict :
        return self.cache.get(hash_name)

    def hset(self, hash_name: str, dict: Dict[str, any]):
        self.cache[hash_name] = dict

    def get(self, key: str) -> str:
        return self.cache.get(key)

    def set(self, key: str, value: str):
        self.cache[key] = value

