def delete_security_group_by_name(aws_client, name):
    security_groups = aws_client.describe_security_groups(
        GroupNames=[name]
    ).get('SecurityGroups', [])

    if len(security_groups) == 0:
        return None
        
    sg_id = security_groups[0].get('GroupId')
    aws_client.delete_security_group(GroupId=sg_id)
    return sg_id

def create_security_group(ec2_client, name, description):
    security_group = ec2_client.create_security_group(GroupName=name, Description=description)
    return security_group
