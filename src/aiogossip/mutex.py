MUTEX = set()


def mutex(mutex_id):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if mutex_id in MUTEX:
                return
            try:
                MUTEX.add(mutex_id)
                return await func(*args, **kwargs)
            finally:
                MUTEX.remove(mutex_id)

        return wrapper

    return decorator
