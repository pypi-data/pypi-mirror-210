from .response.list_hosted_zones import ListHostedZonesResponse
from .response.list_resource_record_sets import ListResourceRecordSetsResponse

class AwsRoute53Client:
    def __init__(self, client):
        self.__client = client

    def list_hosted_zones(self, *args, **kwargs):
        response = self.__client.list_hosted_zones(*args, **kwargs)
        return ListHostedZonesResponse(response)

    def list_resource_record_sets(self, *args, **kwargs):
        response = self.__client.list_resource_record_sets(*args, **kwargs)
        return ListResourceRecordSetsResponse(response)

    def change_resource_record_sets(self, *args, **kwargs):
        self.__client.change_resource_record_sets(*args, **kwargs)

    @staticmethod
    def create(access_key_id = None, secret_access_key = None):
        import boto3

        if (access_key_id == None or secret_access_key == None):
            client = boto3.client('route53')
        else:
            client = boto3.client('route53', access_key_id, secret_access_key)
        return AwsRoute53Client(client)