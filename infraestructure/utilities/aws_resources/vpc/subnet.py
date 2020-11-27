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
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': self.name
                            },
                            {
                                'Key': 'Owner',
                                'Value': 'zezze'
                            },
                        ]
                    },
                ],
            )
            self.id = subnet.id
            self.vpc_id = vpc_id
        except Exception as e:
            print('[ Error ] Creating Subnet', e)
    
    def set_auto_assign_ipv4_ips(self, ec2_client, auto_assign=True):
        if self.id is not None:
            try:
                ec2_client.modify_subnet_attribute(
                    SubnetId=self.id,
                    MapPublicIpOnLaunch={
                        'Value': auto_assign
                    }
                )
            except Exception as e:
                print('[ Erro ] Failed to set auto assign ip...', e)



