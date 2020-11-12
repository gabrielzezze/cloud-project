import constants.aws as aws_contants

class EC2():
    def __init__(self, ec2_client, name, group, type='t2.micro'):
        self.ec2_client = ec2_client
        self.name = name
        self.group = group
        self.type = type
        self.id = None


    def create(self, sg_id, image_id):

        instances = self.ec2_client.create_instances(
            ImageId  = image_id,
            MinCount = 1,
            MaxCount = 1,
            InstanceType = self.type,
            KeyName  = 'zezze_key',
            SecurityGroupIds = [sg_id],
            TagSpecifications = [
                {
                    'ResourceType': 'instance',
                    'Tags': [ 
                        { 'Key': 'Name', 'Value': self.name },
                        { 'Key': 'Owner', 'Value': 'zezze' },
                        { 'Key': 'Type', 'Value': self.group }
                    ]
                }
            ]
        )

        if len(instances) > 0:
            self.id = instances[0].id

    def delete_by_group(self):
        filters = [{ 
                    'Name': 'tag:Type',
                    'Values': [ self.group ]
                },
                {
                    'Name': 'tag:Owner',
                    'Values': [ 'zezze' ]
                }]

        deleted = self.ec2_client.instances.filter(Filters=filters).terminate()
        deleted_ids = []
        if len(deleted) > 0:
            for instance in deleted[0].get('TerminatingInstances', []):
                instance_id = instance.get('InstanceId', None)
                if instance_id:
                    deleted_ids.append(instance_id)

        return deleted_ids

