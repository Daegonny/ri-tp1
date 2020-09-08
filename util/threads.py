import threading
#código obtido de: http://theorangeduck.com/page/synchronized-python
def synchronized(func):

    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func
