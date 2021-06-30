import redis
import pytest


@pytest.fixture(scope="function")
def redis_db():
    """Test that we're using testing redis database,
    load function level fixture, ensure
    database will be flushed after execution of the test function"""
    db_uri = "redis://localhost:6379/15"
    pool = redis.ConnectionPool.from_url(db_uri)
    r = redis.Redis(connection_pool=pool)

    assert r.ping() is True
    yield r

    r.flushdb()
