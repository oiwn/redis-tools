# redis-tools
Various tools to simplify common use cases

[![codecov](https://codecov.io/gh/oiwn/redis-tools/branch/main/graph/badge.svg?token=DV858BK2UL)](https://codecov.io/gh/oiwn/redis-tools)


Helpers and stuff for building web crawlers.

# Installation

```bash

pip install git+https://github.com/oiwn/redis-tools
```


## Redis

- `RedisSetFilter` filter based on redis set.
- `RedisBucketFilter` filter which 'shard' values over few sets.
- `RedisLifoQueue` LIFO queue based on redis
- `RedisUniqueQueue` LIFO queue containing with unique elements


### RedisSetFilter

Trivial implementation of filter using redis set datatype

```python

import redis
from pcg import RedisSetFilter

def redis_set_filter():
    db = redis.from_url("redis://localhost:6379/15")
    f = RedisSetFilter("rdt:set-filter", r=db)

    # adding elements to filter
    f.add("bob")
    assert f.add("alice", "jane") == 2

    # delete element
    f.remove("jane")

    if f.exists("alice"):
        print("Alice already there!")

    if not f.exists("jane"):
        print("Jane not yet come!")

    db.delete("rdt:set-filter")


redis_set_filter()

```

### RedisBucketFilter

Split filter into the buckets, based on murmur hash.

```python
import redis
from pcg import RedisBucketFilter

def redis_bucket_filter():
    db = redis.from_url("redis://localhost:6379/15")
    f = RedisBucketFilter("rdt:bucket-filter", r=db)

    # adding elements to filter
    f.add("alice")
    assert f.add("bob", "jane") == 2

    # delete element
    f.remove("jane")

    # what is bucket for bob?
    bucket_name = f.get_bucket("bob")
    print(bucket_name)

    # info about all available buckets
    print(f.info())

    if f.exists("bob"):
        print("Bob already there!")

    if not f.exists("jane"):
        print("Jane not yet come!")

    keys = db.keys("rdt:bucket-filter:*")
    for key in keys:
        db.delete(key)


redis_bucket_filter()
```

### RedisLifoQueue

Implementation of LIFO queue with json serializable data on top of Redis

```python
import redis
from pcg import RedisLifoQueue


def redis_lifo_queue():
    db = redis.from_url("redis://localhost:6379/15")
    q = RedisLifoQueue("rdt:lifo-queue", r=db)

    # put item into queue
    q.put({"alice": 1})

    # get
    print(q.get())
    #  assert q.get() == {"alice": 1}

    # check if it's empty
    print(q.is_empty())

    # put many items!
    items = [{"b": 1}, {"b": 2}, {"b": 3}]
    q.put_bulk(items)

    # check length
    assert len(q) == 3

    # get one item
    print(q.get())

    # get few items
    print(q.get_bulk(2))

    # check if queue exists and contain something
    print(q.exists("rdt:lifo-queue"))

    db.delete("rdt:lifo-queue")


redis_lifo_queue()
```

# RedisUniqueQueue 

Combination of redis list and set

```python
import redis
from rdt import RedisUniqueQueue

def redis_unique_queue():
    db = redis.from_url("redis://localhost:6379/15")
    q = RedisUniqueQueue(
        "rdt:unique-queue", r=db, keygetter=operator.itemgetter("name")
    )

    print(q.put({"name": "item", "value": 0}))  # should be 0
    print(q.get())

    items = [
        {"name": "item", "value": 1},
        {"name": "key", "value": 1},
        {"name": "elem", "value": 2},
    ]
    q.put_bulk(items)

    assert len(q) == 2

    print(q.get())  # name = key

    db.delete("rdt:unique-queue:queue")
    db.delete("rdt:unique-queue:filter")


redis_unique_queue()
```
