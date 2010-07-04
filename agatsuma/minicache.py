import threading

# I've tried django RWLock. It is very slow, so I prefer
# usual threading.Lock. Yes, it gives exclusive access for readers,
# but faster for five times.
#from agatsuma.third_party.rwlock import RWLock

class MiniCache(object):
    """Implements thread-safe dict-based cache. Intended only for internal usage.
    """
    def __init__(self):
        self._dict = {}
        self._lock = threading.Lock()
        #self._lock = RWLock()

    def set(self, key, value):
        #self._lock.writer_enters()
        self._lock.acquire()
        try:
            self._dict[key] = value
        finally:
            #self._lock.writer_leaves()
            self._lock.release()

    def get(self, key):
        #self._lock.reader_enters()
        self._lock.acquire()
        try:
            return self._dict[key]
        finally:
            #self._lock.reader_leaves()
            self._lock.release()

    def cleanup(self):
        #self._lock.writer_enters()
        self._lock.acquire()
        try:
            self._dict = {}
        finally:
            #self._lock.writer_leaves()
            self._lock.release()

    def remove(self, key):
        #self._lock.writer_enters()
        self._lock.acquire()
        try:
            if key in self._dict:
                del self._dict[key]
        finally:
            #self._lock.writer_leaves()
            self._lock.release()

    def has_key(self, key):
        #self._lock.reader_enters()
        self._lock.acquire()
        try:
            return key in self._dict
        finally:
            #self._lock.reader_leaves()
            self._lock.release()

class EternalInvariantHelper(object):
    """Decorator intended to speed-up absolute invariant functions
    (they always return same result and haven't side effects).
    Caching is based on args, kwargs are not accounted so wrapped
    function should be invariant of kwargs.
    """

    def __init__(self, fn):
        self._fn = fn
        self._cache = MiniCache()

    def __call__(self, *args, **kwargs):
        #key = args[1] # speed-up for 1/4
        key = args # equal to 1. for short tuple
        #key = (args, tuple(kwargs.keys()))
        try:
            #print "cached::::::", key
            return self._cache.get(key)
        except KeyError:
            result = self._fn(*args, **kwargs)
            #print "written:::::::", key
            self._cache.set(key, result)
            return result

def EternalInvariant(function):
    clos = EternalInvariantHelper(function)
    def wrapper(*args, **kwargs):
        return clos(*args, **kwargs)
    return wrapper
