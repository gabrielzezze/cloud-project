from utilities.aws import init_aws_client
from utilities.groups.frontend import Frontend
from utilities.groups.backend import Backend
import boto3

def main():
    aws_client = init_aws_client('ec2', 'us-east-1')
    ec2_client = boto3.resource('ec2', region_name='us-east-1')
    elb_client = boto3.client('elbv2')

    frontend = Frontend(aws_client, ec2_client, elb_client)
    frontend()

    # backend = Backend(aws_client, ec2_client)
    # backend()
    


if __name__ == '__main__':
    main()
