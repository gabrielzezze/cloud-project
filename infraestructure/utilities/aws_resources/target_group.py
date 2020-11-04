def _get_target_group_arn_by_name(elb_client, name) -> str:
    tgs = elb_client.describe_target_groups(
        Names=[name]
    )
    return tgs.get('TargetGroups', [{}])[0].get('TargetGroupArn', None)

def delete_target_group_by_name(elb_client, name):
    tg_arn = _get_target_group_arn_by_name(elb_client, name)

    if tg_arn is not None:
        elb_client.delete_target_group(
            TargetGroupArn=tg_arn
        )

def create_target_group(elb_client, name, protocol, port, vpc_id):
    target_group = elb_client.create_target_group(
        Name=name,
        Protocol=protocol,
        Port=port,
        VpcId=vpc_id,
        Tags=[
            { 'Key': 'Name', 'Value': name },
            { 'Key': 'Owner', 'Value': 'zezze' },
            { 'Key': 'Type', 'Value': 'frontend' }
        ]
    )

    return target_group.get('TargetGroups', [{}])[0].get('TargetGroupArn', None)