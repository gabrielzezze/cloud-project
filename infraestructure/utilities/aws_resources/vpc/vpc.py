from .internet_gateway import InternetGateway
from .route_table import RouteTable
from .subnet import Subnet
from .nat_gateway import NatGateway

class VPC():
    def __init__(self, ec2_resource, name,cidr_block='14.0.0.0/16', private_subnet_cidr_block='14.0.1.0/24', public_subnet_cidr_block='14.0.0.0/24'):
        self.ec2_resource = ec2_resource
        self.cidr_block = cidr_block
        self.public_subnet_cidr_block = public_subnet_cidr_block
        self.private_subnet_cidr_block = private_subnet_cidr_block
        self.name = name
        self.vpc = None

        self._prepare_resources()

    def _prepare_resources(self):
        self.internet_gateway = InternetGateway(self.ec2_resource, f'{self.name}-internet-gateway')

        self.public_subnet = Subnet(self.ec2_resource, f'{self.name}-public-subnet', self.public_subnet_cidr_block)
        self.private_subnet = Subnet(self.ec2_resource, f'{self.name}-private-subnet', self.private_subnet_cidr_block)

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
            vpc.modify_attribute(EnableDnsHostnames={'Value': True})
            vpc.modify_attribute(EnableDnsSupport={'Value': True})
            vpc.reload()

            vpc.wait_until_available()
            self.vpc = vpc

        except Exception as e:
            print('[ Error ] Creating VPC...', e)
    
    def create_subnets(self, ec2_client, availability_zone=None):
        if availability_zone is not None:
            self.public_subnet.create(self.vpc.id, availability_zone)
            self.public_subnet.set_auto_assign_ipv4_ips(ec2_client, True)
        else:
            self.public_subnet.create(self.vpc.id)
            self.public_subnet.set_auto_assign_ipv4_ips(ec2_client, True)

        self.private_subnet.create(self.vpc.id)

    def create_internet_gateway(self):
        self.internet_gateway.create()

    def create_nat_gateway(self, ec2_client, eip_allocation_id):
        self.nat_gateway = NatGateway(ec2_client, f'{self.name}-nat-gateway')
        self.nat_gateway.create(eip_allocation_id, self.public_subnet.id)

    def create_route_tables(self):
        self.private_route_table = RouteTable(self.vpc, f'{self.name}-private-route-table')
        private_route_table_object = list(self.vpc.route_tables.all())[0]
        self.private_route_table.route_table = private_route_table_object

        self.public_route_table = RouteTable(self.vpc, f'{self.name}-public-route-table')
        self.public_route_table.create()

    def handle_private_route_table(self):
        self.private_route_table.associate_subnet(self.private_subnet.id)
        self.private_route_table.create_route('0.0.0.0/0', nat_gateway_id=self.nat_gateway.id)
    
    def handle_public_route_table(self):
        self.public_route_table.associate_subnet(self.public_subnet.id)
        self.public_route_table.create_route('0.0.0.0/0', gateway_id=self.internet_gateway.id)
    
    def handle_internet_gateway(self):
        self.vpc.attach_internet_gateway(
            InternetGatewayId=self.internet_gateway.id
        )
    
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