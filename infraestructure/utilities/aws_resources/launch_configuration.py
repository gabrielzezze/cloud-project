class LaunchConfiguration():
    def __init__(self, as_client, name):
        self.as_client = as_client
        self.name = name

    def delete(self):
        try:
            self.as_client.delete_launch_configuration(
                LaunchConfigurationName=self.name
            )
        except Exception as e:
            print('[ Error ] Deleting Launch Config: ', e)


    def create(self, imageId, keyName, security_groups_ids, instance_type='t2.micro'):
        self.as_client.create_launch_configuration(
            LaunchConfigurationName=self.name,
            ImageId=imageId,
            KeyName=keyName,
            SecurityGroups=security_groups_ids,
            InstanceType=instance_type
        )
