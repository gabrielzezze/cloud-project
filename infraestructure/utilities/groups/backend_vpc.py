from utilities.aws_resources.vpc.vpc import VPC

class BackendVPC():
    def __init__(self, ec2_client, ec2_resource):
        self.ec2_resource = ec2_resource
        self.ec2_client = ec2_client
        self.name = 'zezze-backend-vpc'
        self._prepare_resources()
    
    def _prepare_resources(self):
        self.vpc = VPC(self.ec2_resource, self.name, '14.0.0.0/16')
    
    def __call__(self, eip_alloc_id):
        existing_vpc = self.vpc.get(self.ec2_client)
        if existing_vpc is None:
            print('__BACKEND VPC__')
            self.vpc.create()
            print('Creating Internet gateway...')
            self.vpc.create_internet_gateway()
            print('Creating subnets...')
            self.vpc.create_subnets(self.ec2_client)
            print('Attaching Internet gateway...')
            self.vpc.handle_internet_gateway()
            
            print('Creating NAT gateway...')
            self.vpc.create_nat_gateway(self.ec2_client, eip_alloc_id)
            print('Creating route tables...')
            self.vpc.create_route_tables()

            print('Handling private route table...')
            self.vpc.handle_private_route_table()
            print('Handling public route table...')
            self.vpc.handle_public_route_table()

            return self.vpc.vpc.id
        else:
            existing_vpc.get('VpcId', None)