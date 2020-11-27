from time import sleep

class SecurityGroup():
    def __init__(self, aws_client, ec2_client, name, vpc_id=None):
        self.aws_client = aws_client
        self.ec2_client = ec2_client
        self.name = name
        self.id = None
        self.vpc_id = vpc_id

    def delete(self, delay=5, sg_id=None):
        security_groups = []
        if sg_id is None:
            try:
                security_groups = self.aws_client.describe_security_groups(
                    GroupNames=[self.name]
                ).get('SecurityGroups', [])
            except Exception as e:
                security_groups = []

        if len(security_groups) != 0:
            sg_id = security_groups[0].get('GroupId')
            deleted = False
            while (not deleted):
                try:
                    self.aws_client.delete_security_group(GroupId=sg_id)
                    self.id = sg_id
                    deleted = True
                except:
                    print('Not deleted yet...')
                    sleep(delay)
                    deleted = False
        
        elif sg_id is not None:
            deleted = False
            while (not deleted):
                try:
                    self.aws_client.delete_security_group(GroupId=sg_id)
                    self.id = sg_id
                    deleted = True
                except:
                    print('Not deleted yet...')
                    sleep(delay)
                    deleted = False

    def create(self, description):
        if self.vpc_id is not None:
            security_group = self.ec2_client.create_security_group(
                GroupName=self.name, 
                Description=description,
                VpcId=self.vpc_id
            )
        else:
            security_group = self.ec2_client.create_security_group(
                GroupName=self.name, 
                Description=description
            )
        self.id = security_group.id
        return security_group
