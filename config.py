from collections import namedtuple
from multiprocessing import cpu_count


BIND_ADDRESS = namedtuple('BIND_ADDRESS', ('host', 'port'))('127.0.0.1', 8082)
WORKER_COUNT = cpu_count()
