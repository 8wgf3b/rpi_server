import asyncio
import functools


def aiofy(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        lfunc = lambda: func(*args, **kwargs)
        return loop.run_in_executor(None, lfunc)
    return wrapper
