
from threading import Thread, Lock
from functools import wraps

lock = Lock()

def threaded(**kwargs):
    global lock
    synchronized = kwargs['synchronized'] if 'synchronized' in kwargs else True 

    def decorator(func):
        @wraps(func)
        def run_function_in_tread(*args, **kwargs):
            #print func.__name__
            if synchronized: 
                thr = Thread(target = sync_function, args = args, kwargs = kwargs)
            else:
                thr = Thread(target = func, args = args, kwargs = kwargs)
            thr.start()

        def sync_function(*args, **kwargs):
            lock.acquire()
            func(*args, **kwargs)
            lock.release()

        return run_function_in_tread
    return decorator
