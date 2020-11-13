import asyncio
import functools


def asyncify(_func):
    @functools.wraps(_func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        func = lambda: _func(*args, **kwargs)
        return loop.run_in_executor(None, func)
    return wrapper
