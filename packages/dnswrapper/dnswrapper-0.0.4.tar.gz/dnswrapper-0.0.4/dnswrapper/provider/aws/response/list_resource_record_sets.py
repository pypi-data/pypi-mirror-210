class ListResourceRecordSetsResponse:
    def __init__(self, response):
        self.__response = response

    def isOK(self):
        if self.__response['ResponseMetadata']:
            metadata = self.__response['ResponseMetadata']
            return metadata['HTTPStatusCode'] == 200
        return False

    def getRecordSetsByName(self, name):
        recordSets = []

        def getRecordSetVal(rs):
            return rs['Name'] == name

        if self.isOK():
            recordSets = self.__response['ResourceRecordSets']
            recordSets = list(filter(getRecordSetVal, recordSets))

        return recordSets
