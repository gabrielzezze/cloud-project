def delete_auto_scaling_group_by_name(as_client, name):
    try:
        as_client.delete_auto_scaling_group(
            AutoScalingGroupName=name,
            ForceDelete=True
        )
        return True
    except Exception as e:
        print('[ Error ] Deleting auto scaling group: ', e)
        return False
    

def create_auto_scaling_group(as_client, name, launch_config_name, target_group_arns, minSize, subnets_ids, group):
    as_client.create_auto_scaling_group(
        AutoScalingGroupName=name,
        LaunchConfigurationName=launch_config_name,
        TargetGroupARNs=target_group_arns,
        MinSize=minSize,
        DesiredCapacity=minSize,
        MaxSize=5,
        VPCZoneIdentifier=subnets_ids,
        Tags=[
            {
                'Key': 'owner',
                'Value': 'zezze',
                'PropagateAtLaunch': True
            },
            {
                'Key': 'Type',
                'Value': group,
                'PropagateAtLaunch': True
            }
        ]
    )

    return name

