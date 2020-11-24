class Subnet():
    def __init__(self, ec2_resource, name, cidr_block):
        self.ec2_resource = ec2_resource
        self.name = name
        self.cidr_block = cidr_block
        self.id = None
        self.vpc_id = None

    def create(self, vpc_id):
        try:
            subnet = self.ec2_resource.create_subnet(
                CidrBlock=self.cidr_block, 
                VpcId=vpc_id
            )
            self.id = subnet.id
            self.vpc_id = vpc_id
        except Exception as e:
            print('[ Error ] Creating Subnet', e)

