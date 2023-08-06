from .client import AwsRoute53Client
from ..error.zonecontrol import ZoneControlError
from ..error.awsresponse import AwsResponseError

class AwsZoneManager:
    def __init__(self, zone, aws_client = None):
        if(aws_client == None):
            aws_client = AwsRoute53Client.create()
        self.__client = aws_client
        self.__zone = zone

    def getClient(self):
        return self.__client

    def getZoneId(self):
        response = self.__client.list_hosted_zones()

        name = response.getZoneIdForName(self.__zone)
        if name == None:
            raise ZoneControlError()
        return name

    def getValofRecord(self, record):
        response = self.__client.list_resource_record_sets(
            HostedZoneId=self.getZoneId(),
            StartRecordName=record.fqdn(),
            StartRecordType=record.type()
        )

        if response.isOK():
            recordSets = response.getRecordSetsByName(record.fqdn())
            return  None if len(recordSets) == 0  else recordSets[0]['ResourceRecords'][0]['Value']
        else:
            raise AwsResponseError()

    def upsertRecord(self, record):
        batchedChanges = {
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': record.fqdn(),
                'Type': record.type(),
                'ResourceRecords': [{'Value': "\"{}\"".format(record.val())}],
                'TTL': record.ttl()
            }
        }
        response = self.__client.change_resource_record_sets(
            HostedZoneId=self.getZoneId(),
            ChangeBatch={
                'Changes': [ batchedChanges ]
            })
        return response
