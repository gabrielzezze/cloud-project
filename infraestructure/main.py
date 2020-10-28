from aws import init_aws_client
from constants.aws import get_frontend_image_id
import boto3

def main():
    client = init_aws_client('ec2')

    frontend_security_group_id = None
    for group in client.describe_security_groups()['SecurityGroups']:
        if group.get('GroupName', None) == 'ssh_zezze':
            frontend_security_group_id = group.get('GroupId', None)
        
    if frontend_security_group_id is not None:
        client.delete_security_group(GroupId=frontend_security_group_id)

    ec2 = boto3.resource('ec2', region_name='us-east-1')

    security_group = ec2.create_security_group(GroupName="ssh_zezze", Description='Allow ssh')
    security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
    security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=80, ToPort=8080)

    instance = ec2.create_instances(
        ImageId  = get_frontend_image_id(),
        MinCount = 1,
        MaxCount = 1,
        InstanceType = 't2.micro',
        KeyName  = 'zezze_key',
        SecurityGroupIds = [security_group.id],
        TagSpecifications = [
            {
                'ResourceType': 'instance',
                'Tags': [ { 'Key': 'Name', 'Value': 'zezze-teste' } ]
            }
        ]
    )


if __name__ == '__main__':
    main()
