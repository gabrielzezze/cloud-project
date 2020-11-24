class NatGateway():
    def __init__(self, ec2_client, name):
        self.ec2_client = ec2_client
        self.name = name
        self.id = None
    
    def create(self, allocation_id, subnet_id):
        try:
            res = self.ec2_client.create_nat_gateway(
                AllocationId=allocation_id,
                SubnetId=subnet_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'route-table',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': self.name
                            },
                            {
                                'Key': 'Owner',
                                "Value": 'zezze'
                            }
                        ]
                    }
                ]
            )
            nat_gateway = res.get('NatGateway', None)
            if nat_gateway is not None:
                self.id = nat_gateway.get('NatGatewayId', None)
                return nat_gateway
        except Exception as e:
            print('[ Error ] Creating nat gateway...', e)