from utilities.aws_resources.vpc.vpc import VPC

class BackendVPC():
    def __init__(self, ec2_client, ec2_resource):
        self.ec2_resource = ec2_resource
        self.ec2_client = ec2_client
        self.name = 'zezze-backend-vpc'
    
    def _prepare_resources(self):
        self.vpc = VPC(self.ec2_resource, self.name, '14.0.0.0/24')
    
    def __call__(self):
        existing_vpc = self.vpc.get(self.ec2_client)
        if existing_vpc is None:
            self.vpc.create()
            self.vpc.attach_internet_gateway()
            self.vpc.associate_route_table_to_subnet()
            return self.vpc.id
        else:
            existing_vpc.get('VpcId', None)