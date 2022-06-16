"""Unique queue implementation"""
# pylint: disable=consider-using-f-string
#  import operator
import typing as t

import redis
from rdt.serializers import BaseSerializer, JsonItemSerializer


# operator to get same element
Same = lambda x: x  # pylint: disable=unnecessary-lambda-assignment


class RedisUniqueQueue:
    """Queue with only uniq elements"""

    __slots__ = [
        "__db",
        "__serializer",
        "queue_name",
        "filter_name",
        "keygetter",
    ]

    __serializer: BaseSerializer

    @property
    def db(self) -> redis.client.Redis:
        """Getter for database client"""
        return self.__db

    @property
    def serializer(self) -> BaseSerializer:
        """Current serializer

        :returns: ItemSerializer -- current serializer instance
        """
        return self.__serializer

    def __init__(
        self,
        name: t.Union[str, t.Dict[str, str]],
        r: redis.client.Redis,
        serializer: BaseSerializer = JsonItemSerializer,
        keygetter: t.Callable[[t.Dict], t.Any] = Same,
    ):
        """Trivial LIFO redis queue implementation, with filtering
        store data as serialized json

        :param queue_name: queue key in redis, could be a Dict with keys
            'queue' and 'filter' keys
        :param filter_name: set key in redis
        :param r: redis client instance
        :param serializer: string representation of json library
        :param keygetter: function to access to item key, by default return same
            element
        """
        self.__db = r
        self.__serializer = serializer()

        # define names for queue and filter
        if isinstance(name, dict):
            assert ("queue" in name) and (
                "filter" in name
            ), "name dict should contain 'queue' and 'filter' keys"
            self.queue_name = name["queue"]
            self.filter_name = name["filter"]
        else:
            self.queue_name = f"{name}:queue"
            self.filter_name = f"{name}:filter"

        self.keygetter = keygetter

    def is_empty(self) -> bool:
        """Check if queue is empty

        :returns bool: True if empty and False if not
        """
        return len(self) == 0

    def in_filter(self, value: t.Dict) -> bool:
        """Check if element already in filter"""
        key = self.keygetter(value)
        return bool(self.db.sismember(self.filter_name, key))

    def put(
        self, item: t.Dict
    ) -> int:  # TODO: define item type (int, str, etc)
        """Put item into the queue.

        :param item: serializable item to push into the queue
        :param key: uniq key in item to check against set
        :returns: int -- the length of the list after the push operation
        """
        key = self.keygetter(item)
        if self.db.sismember(self.filter_name, key):
            return 0

        pipe = self.db.pipeline()
        pipe.sadd(self.filter_name, key)
        pipe.rpush(self.queue_name, self.serializer.dumps(item))
        res = pipe.execute()

        # last result contains len of queue after operations
        return int(res[-1])

    def put_bulk(self, items: t.List[t.Dict]) -> bool:
        """Use redis pipelines to push bulk into the queue
        :param items: list of serializables to push into the queue
        :returns: bool - if return fit number of items in queue
        """
        pipe = self.db.pipeline()
        for item in items:
            key = self.keygetter(item)
            if not self.db.sismember(self.filter_name, key):
                pipe.sadd(self.filter_name, key)
                pipe.rpush(self.queue_name, self.serializer.dumps(item))
        res = pipe.execute()
        # if all given `items` already in filter `res` will be []
        if not res:
            return False
        # last result contains len of queue after operations
        return bool(res[-1] == self.__len__())

    def get(self) -> t.Any:  # define type
        """Pop first element from the list
        :returns: dict - serialized item
        """
        item = self.db.lpop(self.queue_name)
        if item is None:
            return None
        return self.serializer.loads(item)

    def get_block(self, timeout=None) -> t.Optional[t.Dict]:
        """Pop item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        item = self.db.blpop(self.queue_name, timeout=timeout)

        if item:
            return dict(self.serializer.loads(item[1]))
        return None

    def get_bulk(self, number_of_items) -> t.List[t.Any]:
        """Remove and return part of list from queue"""
        items_list = []
        for _ in range(number_of_items):
            item = self.db.lpop(self.queue_name)

            if item:
                items_list.append(self.serializer.loads(item))
            else:
                break
        return items_list

    def sizeof(self) -> int:
        """Size of data structure in redis

        :returns: int -- memory used in bytes
        """
        queue_mu = self.db.memory_usage(self.queue_name)  # type: ignore
        filter_mu = self.db.memory_usage(self.filter_name)  # type: ignore
        if queue_mu is None:
            queue_mu = 0
        if filter_mu is None:
            filter_mu = 0
        return int(queue_mu + filter_mu)

    def filter_len(self) -> int:
        """Return number of elements in filter set

        :returns: int -- number of elements in queue
        """
        return int(self.db.scard(self.filter_name))

    def __len__(self) -> int:
        """Queue length.

        :returns: int -- number of elements in queue
        """
        return int(self.db.llen(self.queue_name))

    def __str__(self) -> str:
        """String representation of object

        :returns: str -- class, key name and Redis connection
        """
        return "<RedisUniqueQueue queue_name={} filter_name={} <{}>>".format(
            self.queue_name, self.filter_name, self.db
        )
