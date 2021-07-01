"""Manage counters stored into redis hashmap"""
import redis


class RedisCounters:
    """Store counters into redis hashmap data structure"""

    __slots__ = ["__db", "name"]

    @property
    def db(self):
        """Getter for redis database client"""
        return self.__db

    def __init__(self, name: str, r: redis.client.Redis):
        self.__db = r
        self.name = name

    def inc(self, key: str, val: int = 1):
        """Increment key by value"""
        return self.db.hincrby(self.name, key, amount=val)

    def get(self, key):
        """Return key value"""
        return self.db.hget(self.name, key)

    def keys(self):
        """Return list of keys"""
        return self.db.hkeys(self.name)
