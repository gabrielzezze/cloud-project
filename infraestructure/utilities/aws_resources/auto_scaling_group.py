class AutoScalingGroup():
    def __init__(self, as_client, name, group):
        self.as_client = as_client
        self.name = name
        self.group = group

    def delete(self):
        try:
            self.as_client.delete_auto_scaling_group(
                AutoScalingGroupName=self.name,
                ForceDelete=True
            )
            return True
        except Exception as e:
            print('[ Error ] Deleting auto scaling group: ', e)
            return False
    
    def create(self, launch_config_name, target_group_arns, minSize, subnets_ids):
        self.as_client.create_auto_scaling_group(
            AutoScalingGroupName=self.name,
            LaunchConfigurationName=launch_config_name,
            TargetGroupARNs=target_group_arns,
            MinSize=minSize,
            DesiredCapacity=minSize,
            MaxSize=5,
            VPCZoneIdentifier=subnets_ids,
            Tags=[
                {
                    'Key': 'Owner',
                    'Value': 'zezze',
                    'PropagateAtLaunch': True
                },
                {
                    'Key': 'Type',
                    'Value': self.group,
                    'PropagateAtLaunch': True
                }
            ]
        )
        return self.name

