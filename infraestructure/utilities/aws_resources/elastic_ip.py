class ElasticIP():
    def __init__(self, aws_client, name):
        self.aws_client = aws_client
        self.name = name
        self.ip = None
        self.allocation_id = None
    
    def get_ip(self):
        elastics_ips = self.aws_client.describe_addresses(
            Filters=[{
                'Name': "tag:Name",
                'Values': [self.name]
            }]
        )

        addresses = elastics_ips.get('Addresses', None)
        if addresses is not None and len(addresses) > 0:
            alloc_id = addresses[0].get('AllocationId', None)
            ip = addresses[0].get('PublicIp', None)
            self.allocation_id = alloc_id
            self.public_ip = ip

        return self.public_ip
    
    def _handle_tag_association(self):
        if self.allocation_id is not None:
            self.aws_client.create_tags(
                Resources=[self.allocation_id],
                Tags=[
                    { 'Key': 'Name', 'Value': self.name }
                ])

    def create(self):
        try:
            res = self.aws_client.allocate_address(
                Domain='vpc'
            )
            self.allocation_id = res.get('AllocationId', None)
            self.ip = res.get('PublicIp', None)
            self._handle_tag_association()

        except Exception as e:
            print('[ Error ] Creating Elastic IP: ', e)
    
    def delete(self):
        try:
            res = self.aws_client.release_address(
                AllocationId=self.allocation_id
            )
        
        except Exception as e:
            print('[ Error ] Deleting elastic IP: ', e)




        