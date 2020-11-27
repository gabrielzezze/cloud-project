from utilities.aws_resources.vpc.vpc import VPC
from utilities.aws_resources.elastic_ip import ElasticIP

class BackendVPC():
    def __init__(self, ec2_client, ec2_resource):
        self.ec2_resource = ec2_resource
        self.ec2_client = ec2_client
        self.name = 'zezze-backend-vpc'
        self.vpc_cidr_block = '14.0.0.0/16'
        self.vpc_private_subnet_cidr_block = '14.0.1.0/24'
        self.vpc_public_subnet_cidr_block = '14.0.0.0/24'
        self._prepare_resources()
    
    def _prepare_resources(self):
        self.vpc = VPC(self.ec2_resource, self.name, self.vpc_cidr_block)
        self.nat_gateway_elastic_ip = ElasticIP(self.ec2_client, 'zezze-backend-vpc-nat-gateway-elastic-ip')
    
    def __call__(self):
        existing_vpc = self.vpc.get(self.ec2_client)
        if existing_vpc is None:
            self.nat_gateway_elastic_ip.get_ip()
            print('__BACKEND VPC__')

            print('Checking for nat gateway elastic ip...')
            if self.nat_gateway_elastic_ip.allocation_id is None:
                print('[ INFO ] Natgateway elastic ip not found, creating one now...')
                self.nat_gateway_elastic_ip.create()

            print('Creating vpc...')
            self.vpc.create()
            print('Creating Internet gateway...')
            self.vpc.create_internet_gateway()

            print('Creating subnets...')
            self.vpc.create_subnets(self.ec2_client)
            print('Attaching Internet gateway...')
            self.vpc.handle_internet_gateway()
            
            print('Creating NAT gateway...')
            self.vpc.create_nat_gateway(self.ec2_client, self.nat_gateway_elastic_ip.allocation_id)
            print('Creating route tables...')
            self.vpc.create_route_tables()

            print('Handling private route table...')
            self.vpc.handle_private_route_table()
            print('Handling public route table...')
            self.vpc.handle_public_route_table()

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
            
            return vpc_resource, private_subnet, public_subnet