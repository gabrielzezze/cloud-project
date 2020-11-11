def delete_launch_config_by_name(as_client, name):
    try:
        as_client.delete_launch_configuration(
            LaunchConfigurationName=name
        )
    except Exception as e:
        print('[ Error ] Deleting Launch Config: ', e)


def create_launch_configuration(as_client, name, imageId, keyName, security_groups_ids, instance_type='t2.micro'):
    as_client.create_launch_configuration(
        LaunchConfigurationName=name,
        ImageId=imageId,
        KeyName=keyName,
        SecurityGroups=security_groups_ids,
        InstanceType=instance_type
    )
