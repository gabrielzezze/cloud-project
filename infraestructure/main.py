from aws import init_aws_client
import boto3

def main():
    init_aws_client('ec2')

    ec2 = boto3.resource('ec2', region_name='us-east-1')

    security_group = ec2.create_security_group(GroupName="ssh_zezze",Description='Allow ssh')
    security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
    
    instance = ec2.create_instances(
        ImageId='ami-0dba2cb6798deb6d8',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='zezze_key',
        SecurityGroupIds=[security_group.id],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [ { 'Key': 'Name', 'Value': 'zezze-teste' } ]
            }
        ]
    )

if __name__ == '__main__':
    main()
