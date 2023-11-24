import collections

# FIXME: use time-based mutexes
MUTEX_CAPACITY = 1024
MUTEX = collections.defaultdict(lambda: collections.deque(maxlen=MUTEX_CAPACITY))


def mutex(mutex_id, owner=None):
    def decorator(func):
        mutexes = MUTEX[owner or func]

        async def wrapper(*args, **kwargs):
            if mutex_id in mutexes:
                return

            mutexes.append(mutex_id)
            return await func(*args, **kwargs)

        return wrapper

    return decorator
