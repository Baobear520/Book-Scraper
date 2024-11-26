import time


def runtime_counter(func):
    """A decorator for checking script's runtime"""

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args,*kwargs)
        end = time.perf_counter()
        duration = end - start
        print(f"Script runtime: {duration:.2f} seconds")
    return wrapper


