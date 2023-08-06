from .local_client import LocalClient


class LocalResolver:
    def __init__(self, domain, client = None):
        if (client == None):
            client = LocalClient()
        self.__domain = domain
        self.__client = client

    def fetchTXTRecords(self, query_string):
        answers = self.__client.resolveTXTRecord(query_string)
        massagedAnswers = []
        for answer in answers:
            massagedAnswers.append(answer  + "." + self.__domain)
        return massagedAnswers
        
    def queryForIP(self, query_string):
        return self.__client.getHostByName(query_string)