import time


def memoize(func):
    cache = {}

    def wrapper(*args):
        func_cache = cache.get(func.__name__)
        if func_cache is None:
            func_cache = {}
            cache[func.__name__] = func_cache

        if args in func_cache:
            return func_cache[args]
        else:
            result = func(*args)
        func_cache[args] = result
        return result
    return wrapper


def timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[{func.__name__}] took {end_time - start_time} secs")
        return result
    return wrapper
