from .lookup_error import LookupError

import dns.resolver
import socket

class LocalClient:
    def getHostByName(self, query_string):
        try:
            return socket.gethostbyname(query_string)
        except socket.gaierror as e:
            raise LookupError(e)

    def resolveTXTRecord(self, record_string):
        try:
            answers = []
            for answer in dns.resolver.resolve(record_string,"TXT").rrset:
                answers.append(answer.to_text().strip('"'))
            return answers
        except dns.resolver.NXDOMAIN as e:
            raise LookupError(e)
