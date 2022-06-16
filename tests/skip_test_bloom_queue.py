"""Tests for bloom queue"""
# pylint: disable=redefined-outer-name,invalid-name
import operator

import pytest
from redisbloom import client as RedisBloom

from rdt.bloom_queue import RedisBloomQueue


@pytest.fixture(scope="function")
def rdb():
    """Test that we're using testing redis database,
    load function level fixture, ensure
    database will be flushed after execution of the test function"""
    db = "redis://localhost:6379/15"
    r = RedisBloom.Client.from_url(db)

    assert r.ping() is True
    yield r

    r.flushdb()


@pytest.mark.skip(reason="check, looks like library not working")
def test_redis_bloom_queue(rdb):
    """Test bloom queue"""
    q = RedisBloomQueue(
        "rdt:test-bloom-queue", r=rdb, keygetter=operator.itemgetter("_id")
    )

    # check db property
    assert isinstance(q.db, RedisBloom.Client)

    # put / get
    assert q.put({"_id": 0, "alice": 1}) == 1
    assert q.get() == {"_id": 0, "alice": 1}

    # check if empty
    assert q.is_empty() is True

    # get from empty queue
    assert q.get() is None

    # add few
    assert q.put({"_id": 1, "a": 1}) == 1
    assert q.put({"_id": 2, "a": 2}) == 2

    # this should be filtered
    assert q.put({"_id": 0, "a": 1000}) == 0
    assert q.put({"_id": 1, "a": 2000}) == 0

    # check not empty
    assert q.is_empty() is False

    # check in filter
    assert q.in_filter({"_id": 0, "bob": 1}) is True
    assert q.in_filter({"_id": 3, "bob": 1}) is False

    # and len
    assert len(q) == 2

    # put bulk 3 elements
    items = [{"_id": 3, "b": 1}, {"_id": 4, "b": 2}, {"_id": 5, "b": 3}]
    assert q.put_bulk(items) is True

    # len
    assert len(q) == 5

    # sizeof
    assert q.sizeof() > 0

    # get bulk
    assert len(q.get_bulk(2)) == 2
    assert len(q.get_bulk(10)) == 3
    assert q.is_empty() is True

    # sizeof should return None since there is no key
    assert q.sizeof() > 0  # we have some elements in filter
    assert q.filter_len() == 1378624

    # print
    assert "RedisBloomQueue" in str(q)
    assert "rdt:test-bloom-queue:queue" in str(q)


def test_redis_bloom_queue_keygetter(rdb):
    """Test unique queue"""
    q = RedisBloomQueue(
        "rdt:test-bloom-queue",
        r=rdb,
        keygetter=lambda x: x["payload"]["key"],
    )

    # put / get
    assert q.put({"_id": 0, "alice": 1, "payload": {"key": "a"}}) == 1
    assert q.get()["payload"]["key"] == "a"

    # check if empty
    assert q.is_empty() is True

    # get from empty queue
    assert q.get() is None

    # put bulk 3 elements
    items = [
        {"payload": {"key": "b"}, "_id": 1},
        {"payload": {"key": "c"}, "_id": 2},
        {"payload": {"key": "c"}, "_id": 3},
    ]
    assert q.put_bulk(items) is True

    # len
    assert len(q) == 3

    # check in filter
    assert q.in_filter({"payload": {"key": "b"}, "bob": 1}) is True
    assert q.in_filter({"payload": {"key": "d"}, "bob": 1}) is False

    # sizeof
    assert q.sizeof() > 0

    # get bulk
    assert len(q.get_bulk(2)) == 2
    assert len(q.get_bulk(10)) == 1
    assert q.is_empty() is True


def test_redis_bloom_queue_kegsetter_default_value(rdb):
    """Test unique queue"""
    q = RedisBloomQueue("rdt:test-bloom-queue", r=rdb)

    assert q.is_empty() is True

    # get from empty queue
    assert q.get() is None

    # put bulk 3 elements
    items = ["a", "b", "c"]
    assert q.put_bulk(items) is True

    # len
    assert len(q) == 3

    # check in filter
    assert q.in_filter("a") is True
    assert q.in_filter("d") is False

    assert q.get() == "a"


def test_redis_bloom_queue_bulk_items_already_in_filter(rdb):
    """Test put_bulk of items already in filter"""

    q = RedisBloomQueue("rdt:test-bloom-queue", r=rdb)

    items = ["a", "b", "c"]

    assert q.put_bulk(items) is True
    assert q.put_bulk(items) is False
