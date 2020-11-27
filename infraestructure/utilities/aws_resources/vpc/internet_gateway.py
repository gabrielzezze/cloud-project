class InternetGateway():
    def __init__(self, ec2_resource, name):
        self.name = name
        self.id = None
        self.ec2_resource = ec2_resource

    def create(self):
        try:
            internet_gateway = self.ec2_resource.create_internet_gateway(
                TagSpecifications=[
                    {
                        'ResourceType': 'internet-gateway',
                        'Tags': [ {'Key': 'Name', 'Value': self.name } ]
                    }
                ]
            )
            self.id = internet_gateway.id
        except Exception as e:
                print('[ Error ] Creating Internet Gateway...', e)