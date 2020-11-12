class SecurityGroup():
    def __init__(self, aws_client, ec2_client, name):
        self.aws_client = aws_client
        self.ec2_client = ec2_client
        self.name = name
        self.id = None

    def delete(self):
        try:
            security_groups = self.aws_client.describe_security_groups(
                GroupNames=[self.name]
            ).get('SecurityGroups', [])
        except Exception as e:
            security_groups = []

        if len(security_groups) != 0:
            sg_id = security_groups[0].get('GroupId')
            self.aws_client.delete_security_group(GroupId=sg_id)
            self.id = sg_id

    def create(self, description):
        security_group = self.ec2_client.create_security_group(GroupName=self.name, Description=description)
        self.id = security_group.id
        return security_group
