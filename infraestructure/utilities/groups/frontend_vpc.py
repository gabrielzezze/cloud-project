from utilities.aws_resources.vpc.vpc import VPC
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.aws_resources.vpc.subnet import Subnet

class FrontendVPC():
    def __init__(self, ec2_client, ec2_resource):
        self.ec2_resource = ec2_resource
        self.ec2_client = ec2_client
        self.name = 'zezze-frontend-vpc'
        self.vpc_cidr_block = '14.10.0.0/16'
        self.vpc_private_subnet_cidr_block = '14.10.1.0/24'
        self.vpc_public_subnet_cidr_block = '14.10.0.0/24'
        self._prepare_resources()

    def _prepare_resources(self):
        self.vpc = VPC(self.ec2_resource, self.name, self.vpc_cidr_block, self.vpc_private_subnet_cidr_block, self.vpc_public_subnet_cidr_block)

    def handle_second_public_subnet(self):
        self.second_public_subnet = Subnet(self.ec2_resource, 'zezze-frontend-vpc-second-public-subnet', '14.10.2.0/24')
        self.second_public_subnet.get(self.ec2_client)
        if self.second_public_subnet.id is None:
            self.second_public_subnet.create(self.vpc.id, 'us-east-1b')
        
        res = self.ec2_client.describe_route_tables(
            Filters=[
                {
                    'Name': 'association.subnet-id',
                    'Values': [
                        self.public_subnet.id
                    ]
                }
            ]
        )
        route_table_id = res.get('RouteTables', [{}])[0].get('RouteTableId', None)
        if route_table_id:
            frontend_public_route_table = self.ec2_client.RouteTable(route_table_id)
            frontend_public_route_table.associate_with_subnet(
                    SubnetId=self.second_public_subnet.id
                )


    def handle_public_route_table(self, network_interface_id):
        res = self.ec2_client.describe_route_tables(
            Filters=[
                {
                    'Name': 'association.subnet-id',
                    'Values': [
                        self.public_subnet.id
                    ]
                }
            ]
        )
        route_table_id = res.get('RouteTables', [{}])[0].get('RouteTableId', None)
        if route_table_id:
            try:
                route = self.ec2_resource.Route(route_table_id, '14.0.0.0/16')
                if route:
                    route.replace(NetworkInterfaceId=network_interface_id)
            except:
                route = None
            if route is None:
                frontend_public_route_table = self.ec2_resource.RouteTable(route_table_id)
                frontend_public_route_table.create_route(
                    DestinationCidrBlock='14.0.0.0/16', 
                    NetworkInterfaceId=network_interface_id
                )

    def __call__(self):
        existing_vpc = self.vpc.get(self.ec2_client)
        if existing_vpc is None:
            print('__FRONTEND VPC__')

            print('Creating vpc...')
            self.vpc.create()
            print('Creating Internet gateway...')
            self.vpc.create_internet_gateway()

            print('Creating subnets...')
            self.vpc.create_subnets(self.ec2_client, 'us-east-1a')
            print('Attaching Internet gateway...')
            self.vpc.handle_internet_gateway()
            
            print('Creating route tables...')
            self.vpc.create_route_tables()

            print('Handling public route table...')
            self.vpc.handle_public_route_table()

            self.private_subnet = self.vpc.private_subnet
            self.public_subnet = self.vpc.public_subnet
            self.vpc = self.vpc.vpc

            return self.vpc.vpc, self.vpc.public_subnet, self.vpc.private_subnet

        else:
            vpc_id = existing_vpc.get('VpcId', None)
            vpc_resource = self.ec2_resource.Vpc(vpc_id)
            vpc_subnets = vpc_resource.subnets.all()

            private_subnet = None
            public_subnet = None
            for subnet in vpc_subnets:
                cidr_block = subnet.cidr_block
                if cidr_block == self.vpc_private_subnet_cidr_block:
                    private_subnet = subnet
                elif cidr_block == self.vpc_public_subnet_cidr_block:
                    public_subnet = subnet

            self.private_subnet = private_subnet
            self.public_subnet = public_subnet
            self.vpc = vpc_resource

            return vpc_resource, private_subnet, public_subnet