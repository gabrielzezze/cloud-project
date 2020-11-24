class RouteTable():
    def __init__(self, vpc, name):
        self.vpc = vpc
        self.name = name
        self.route_table = None
    
    def create(self):
        try:
            routetable = self.vpc.create_route_table(
                TagSpecifications=[
                    {
                        'ResourceType': 'route-table',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': self.name
                            }
                        ]
                    }
                ]
            )
            self.route_table = routetable
        except Exception as e:
            print('[ Error ] Creating route table...')
    
    def associate_subnet(self, subnet_id):
        if self.route_table is not None:
            try:
                self.route_table.associate_with_subnet(
                    SubnetId=subnet_id
                )
            except Exception as e:
                print('[ Error ] Associating subnet to route table...', e)

    def create_route(self, cidr_block, gateway_id=None, nat_gateway_id=None, instance_id=None):
        if self.route_table is not None:
            try:
                route = self.route_table.create_route(
                    DestinationCidrBlock=cidr_block, 
                    GatewayId=gateway_id,
                    NatGatewayId=nat_gateway_id,
                    InstanceId=instance_id
                )
            except Exception as e:
                print('[ Error ] Creating route...', e)
