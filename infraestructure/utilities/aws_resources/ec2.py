import constants.aws as aws_contants

def create_ec2_instance(ec2_client, name, sg_id, image_id, group ,type='t2.micro'):

    instance = ec2_client.create_instances(
        ImageId  = image_id,
        MinCount = 1,
        MaxCount = 1,
        InstanceType = type,
        KeyName  = 'zezze_key',
        SecurityGroupIds = [sg_id],
        TagSpecifications = [
            {
                'ResourceType': 'instance',
                'Tags': [ 
                    { 'Key': 'Name', 'Value': name },
                    { 'Key': 'Owner', 'Value': 'zezze' },
                    { 'Key': 'Type', 'Value': group }
                ]
            }
        ]
    )

    return instance[0].id

def delete_ec2_instances_by_group(ec2_client, group):
    filters = [
        { 
            'Name': 'tag:Type',
            'Values': [ group ]
        },
        {
            'Name': 'tag:Owner',
            'Values': [ 'zezze' ]
        }
    ]

    deleted = ec2_client.instances.filter(Filters=filters).terminate()
    deleted_ids = []
    if len(deleted) == 0:
        return []
    for instance in deleted[0].get('TerminatingInstances', []):
        instance_id = instance.get('InstanceId', None)
        if instance_id:
            deleted_ids.append(instance_id)

    return deleted_ids

