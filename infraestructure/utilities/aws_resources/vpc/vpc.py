from .internet_gateway import InternetGateway
from .route_table import RouteTable
from .subnet import Subnet
from .nat_gateway import NatGateway

class VPC():
    def __init__(self, ec2_resource, name,cidr_block='14.0.0.0/24', private_cidr_block='14.0.1.0/24'):
        self.ec2_resource = ec2_resource
        self.cidr_block = cidr_block
        self.private_cidr_block = private_cidr_block
        self.name = name
        self.vpc = None

        self._prepare_resources()

    def _prepare_resources(self):
        self.internet_gateway = InternetGateway(self.ec2_resource, f'{self.name}-internet-gateway')
        self.internet_route_table = RouteTable(self.vpc, f'{self.name}-internet-gateway-route-table')
        self.public_subnet = Subnet(self.ec2_resource, f'{self.name}-public-subnet', self.cidr_block)

        self.private_route_table = RouteTable(self.vpc, f'{self.name}-private-route-table')
        self.private_subnet = Subnet(self.ec2_resource, f'{self.name}-private-subnet', self.private_cidr_block)

    def attach_internet_gateway(self, gateway_instance_id):
        if self.vpc is not None:
            try:
                self.internet_gateway.create()
                self.vpc.attach_internet_gateway(
                    InternetGatewayId=self.internet_gateway.id
                )

                self.internet_route_table.create()
                self.internet_route_table.create_route(
                    cidr_block='0.0.0.0/0',
                    gateway_id=self.internet_gateway.id
                )

                self.internet_route_table.create_route(
                    cidr_block='0.0.0.0/0',
                    instance_id=gateway_instance_id
                )
            except Exception as e:
                print('[ Error ] Creating VPC...', e)
        else:
            print('[ Error ] VPC is None...')

    def attach_nat_gateway(self, ec2_client, allocation_id):
        self.nat_gateway = NatGateway(ec2_client, f'{self.name}-nat-gateway')
        self.nat_gateway.create(allocation_id, self.private_subnet.id)
        self.private_route_table.create_route(
            cidr_block='0.0.0.0/0',
            gateway_id=self.nat_gateway.id
        )
        self.private_route_table.create_route(
            cidr_block=self.cidr_block,
            
        )

    def associate_route_tables_to_subnets(self):
        if self.vpc is not None:
            try:
                self.public_subnet.create(self.vpc.id)
                self.internet_route_table.associate_subnet(self.public_subnet.id)

                self.private_route_table.create()
                self.private_subnet.create(self.vpc.id)
                self.private_route_table.associate_subnet(self.private_subnet.id)
            except Exception as e:
                print('[ Error ] Associating subnet to route table...')

    def create(self):
        try:
            vpc = self.ec2_resource.create_vpc(
                CidrBlock=self.cidr_block,
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc',
                        'Tags': [
                            { 'Key': 'Name','Value': self.name},
                            { 'Key': 'Owner','Value': 'zezze'}
                        ]
                    },
                ]
            )
            vpc.wait_until_available()
            self.vpc = vpc
        except Exception as e:
            print('[ Error ] Creating VPC...', e)

    def get(self, ec2_client):
        try:
            res = ec2_client.describe_vpcs(
                Filters=[
                    { 'Name': 'tag:Name', 'Values': [self.name] },
                    { 'Name': 'tag:Owner', 'Values': ['zezze'] }
                ]
            )
            vpcs = res.get('Vpcs', [])
            if len(vpcs) > 0:
                return vpcs[0]

            return None

        except Exception as e:
            print('Could not fin VPC...', e)
            return None