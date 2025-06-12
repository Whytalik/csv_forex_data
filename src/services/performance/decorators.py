import time
from functools import wraps


def async_timing_decorator(func):
    """Decorator to time async functions"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ {func.__name__} completed in {duration:.2f}s")
        return result

    return wrapper


def timing_decorator(func):
    """Decorator to time regular functions"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ {func.__name__} completed in {duration:.2f}s")
        return result

    return wrapper
