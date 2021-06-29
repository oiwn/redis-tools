"""Test filters"""
# pylint: disable=missing-function-docstring
import redis

from rdt import RedisSetFilter, RedisBucketFilter
from tests.fixtures import redis_db


rdb = redis_db


def test_redis_set_filter(rdb):
    f = RedisSetFilter("rdt:test-set", r=rdb)

    # check db property
    assert isinstance(f.db, redis.client.Redis)

    # add single value
    assert f.add("alice") == 1
    assert len(f.to_set()) == len(f) == 1
    assert isinstance(f.to_set(), set)
    assert f.to_set() == set(["alice"])

    # add few values
    assert f.add("bob", "jane") == 2
    assert f.add("bob", "jane") == 0
    assert len(f) == 3

    # remove value
    assert f.remove("jane") is True
    assert f.remove("john") is False
    assert len(f) == 2

    # check existance
    assert f.exists("alice") is True
    assert f.exists("jane") is False

    # data structure in memory size
    f.add("many", "other", "people", "walking", "around")
    assert len(f) == 7
    assert f.sizeof() > 300

    # check str
    assert "RedisSetFilter" in str(f)
    assert "rdt:test-set" in str(f)


def test_redis_bucket_filter(rdb):
    f = RedisBucketFilter("rdt:test-bucket", r=rdb, bucket_digits=1)

    # check db property
    assert isinstance(f.db, redis.client.Redis)

    # bucket number
    assert f.get_bucket("original__barbie") == "4"

    # add single value
    assert f.add("alice") == 1
    assert f.exists("alice") is True
    assert f.exists("bob") is False

    # add few values
    assert f.add("bob", "john", "jane") == 3
    assert f.add("bob", "john", "jane") == 0
    assert len(f) == 4

    # remove value
    assert f.remove("jane") is True
    assert f.remove("tom") is False

    # check existance
    assert f.exists("alice") is True
    assert f.exists("jane") is False

    # data structure in memory size
    f.add("dome", "roland", "krot", "bes", "paperclip")
    assert len(f) == 8
    assert f.sizeof() > 300

    # check info about buckets
    assert len(f.info()) == 5
    assert f.info()["rdt:test-bucket:1"] == 3
    assert f.info()["rdt:test-bucket:4"] == 2

    # check str
    assert "RedisBucketFilter" in str(f)
    assert "rdt:test-bucket" in str(f)
