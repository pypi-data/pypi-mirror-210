class ListHostedZonesResponse:
    def __init__(self, response):
        self.__response = response

    def getZoneIdForName(self, name):
        for zone in self.__response['HostedZones']:
            if zone['Name'] == name:
                return zone['Id']
        return None