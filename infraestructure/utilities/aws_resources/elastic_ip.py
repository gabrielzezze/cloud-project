class ElasticIP():
    def __init__(self, aws_client, name):
        self.aws_client = aws_client
        self.name = name
        self.ip = None
    
    def get_ip(self):
        elastics_ips = self.aws_client.describe_addresses(
            Filters=[{
                'Name': "tag:Name",
                'Values': [self.name]
            }]
        )

        addresses = elastics_ips.get('Addresses', None)
        if addresses is not None and len(addresses) > 0:
            ip = addresses[0].get('PublicIp', None)
            self.public_ip = ip

        return self.public_ip
