class NatGateway():
    def __init__(self, ec2_client, name):
        self.ec2_client = ec2_client
        self.name = name
        self.id = None
    
    def create(self, allocation_id, subnet_id):
        waiter = self.ec2_client.get_waiter('nat_gateway_available')
        try:
            res = self.ec2_client.create_nat_gateway(
                AllocationId=allocation_id,
                SubnetId=subnet_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'natgateway',
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
                waiter.wait(
                    NatGatewayIds=[self.id]
                )
                return nat_gateway
        except Exception as e:
            print('[ Error ] Creating nat gateway...', e)