"""Benchmark redis tools"""
import timeit
import redis
from rdt import RedisLifoQueue

REDIS_DB = "redis://localhost:6379/15"


def data_generator(number, bulk=False):
    """Generate dummy data"""
    if not bulk:
        for index in range(number):
            yield {"count": index, "value": "Hi!"}
    else:
        bulk_elems = []

        for index in range(number):

            if (index != 0) and (index % 10) == 0:
                yield bulk_elems

                bulk_elems = [{"count": index, "value": "Hi!"}]
            else:
                bulk_elems.append({"count": index, "value": "Hi!"})

        if bulk_elems:
            yield bulk_elems


def benchmark_lifo_queue(requests_num=100):
    """Benchmark redis queue"""
    pool = redis.ConnectionPool.from_url(REDIS_DB)
    r = redis.Redis(connection_pool=pool)
    queue = RedisLifoQueue("rdt-bench:queue", r=r)

    data = data_generator(requests_num)

    for elem in data:
        queue.put(elem)

    assert len(queue) == requests_num

    for index in range(requests_num):
        elem = queue.get()
        assert elem["count"] == index

    assert len(queue) == 0
    r.delete("rdt-bench-queue")


def benchmark_lifo_queue_bulk(requests_num=100):
    """Benchmark redis queue"""
    pool = redis.ConnectionPool.from_url(REDIS_DB)
    r = redis.Redis(connection_pool=pool)
    queue = RedisLifoQueue("rdt-bench:queue", r=r)

    data = data_generator(requests_num, bulk=True)
    for elements in data:
        queue.put_bulk(elements)

    assert len(queue) == requests_num

    for _ in range(requests_num // 10):
        elems = queue.get_bulk(10)
        assert len(elems) == 10

    assert len(queue) == 0
    r.delete("rdt-bench-queue")


if __name__ == "__main__":
    print(
        "RedisLifoQueue put/get performance: {}".format(
            timeit.timeit(
                "benchmark_lifo_queue()",
                setup="from __main__ import benchmark_lifo_queue",
                number=100,
            )
        )
    )
    print(
        "RedisLifoQueue put_bulk/get_bulk performance: {}".format(
            timeit.timeit(
                "benchmark_lifo_queue_bulk()",
                setup="from __main__ import benchmark_lifo_queue_bulk",
                number=100,
            )
        )
    )
