import time
import logging

logger = logging.getLogger(__name__)

def profiler(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__} took {end - start:.2f} seconds')
        # logger.info(f'{func.__name__} took {end - start:.2f} seconds')
        return result
    return wrapper
