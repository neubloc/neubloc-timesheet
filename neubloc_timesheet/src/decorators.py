
from threading import Thread
from functools import wraps

def threaded(func):
    @wraps(func)
    def run_function_in_tread(*args, **kwargs):
        thr = Thread(target = func, args = args, kwargs = kwargs)
        thr.start()
    return run_function_in_tread
