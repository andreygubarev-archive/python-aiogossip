import collections

MUTEX_CAPACITY = 100
MUTEX = collections.defaultdict(lambda: collections.deque(maxlen=MUTEX_CAPACITY))


def mutex(mutex_id):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if mutex_id in MUTEX[func]:
                return
            try:
                MUTEX[func].append(mutex_id)
                return await func(*args, **kwargs)
            finally:
                MUTEX[func].remove(mutex_id)

        return wrapper

    return decorator
