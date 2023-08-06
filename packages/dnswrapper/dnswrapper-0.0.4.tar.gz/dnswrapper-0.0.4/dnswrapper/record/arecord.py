from .record import Record

class ARecord:
    def __init__(self, name, ip=None):
        self.__record = Record("A", name, ip)

    def __getattr__(self, attr):
        if hasattr(self.__record, attr):
            def wrapper(*args, **kw):
                return getattr(self.__record, attr)(*args, **kw)
            return wrapper
        raise AttributeError(attr)
