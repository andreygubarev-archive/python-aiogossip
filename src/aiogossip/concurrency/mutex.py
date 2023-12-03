import collections
import functools
import time

from ..config import MUTEX_TTL

MUTEX = collections.defaultdict(dict)


def mutex(owner, mutex_id, mutex_ttl=MUTEX_TTL):
    """
    Decorator that provides mutual exclusion for a function based on the owner and mutex_id.

    Args:
        owner (str): The owner of the mutex.
        mutex_id (str): The identifier of the mutex.
        mutex_ttl (int, optional): The time-to-live (TTL) for the mutex in seconds. Defaults to MUTEX_TTL.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            mut = MUTEX[owner].get(mutex_id)
            if mut:
                if time.time() - mut > mutex_ttl:
                    MUTEX[owner][mutex_id] = time.time()
                    return await func(*args, **kwargs)
                else:
                    return
            else:
                MUTEX[owner][mutex_id] = time.time()
                return await func(*args, **kwargs)

        return wrapper

    return decorator
