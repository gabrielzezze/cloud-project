class TargetGroup():
    def __init__(self, elb_client, name, group):
        self.elb_client = elb_client
        self.name = name
        self.group = group

    def _get_arn_by_name(self):
        tgs = self.elb_client.describe_target_groups(
            Names=[self.name]
        )
        self.arn = tgs.get('TargetGroups', [{}])[0].get('TargetGroupArn', None)

    def delete(self):
        self._get_arn_by_name()

        if self.arn is not None:
            self.elb_client.delete_target_group(
                TargetGroupArn=self.arn
            )

    def create(self, protocol, port, vpc_id):
        target_group = self.elb_client.create_target_group(
            Name=self.name,
            Protocol=protocol,
            Port=port,
            VpcId=vpc_id,
            Tags=[
                { 'Key': 'Name', 'Value': self.name },
                { 'Key': 'Owner', 'Value': 'zezze' },
                { 'Key': 'Type', 'Value': self.group }
            ]
        )

        self.arn = target_group.get('TargetGroups', [{}])[0].get('TargetGroupArn', None)