class Record:
    def __init__(self, type, name, ip=None, ttl = 60):
        self.__type = type
        self.__name = name
        self.__ip = ip
        self.__ttl = ttl

    def fqdn(self):
        return self.__name

    def val(self):
        return self.__ip

    def type(self):
        return self.__type

    def ttl(self):
        return self.__ttl