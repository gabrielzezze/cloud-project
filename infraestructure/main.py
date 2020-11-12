from utilities.aws import init_aws_client
from utilities.groups.frontend import Frontend
# from utilities.groups.backend import Backend
import boto3
import sys

def handle_frontend_infraestructure():
    aws_client = init_aws_client('ec2', 'us-east-1')
    ec2_client = boto3.resource('ec2', region_name='us-east-1')
    elb_client = init_aws_client('elbv2', 'us-east-1')
    as_client = init_aws_client('autoscaling', 'us-east-1')

    frontend = Frontend(aws_client, ec2_client, elb_client, as_client)
    frontend()

def handle_backend_infraestructrue():
    pass
    # aws_client = init_aws_client('ec2', 'us-east-2')
    # ec2_client = boto3.resource('ec2', region_name='us-east-2')
    # backend = Backend(aws_client, ec2_client)
    # backend()

if __name__ == '__main__':
    args = sys.argv

    if '--frontend' in args:
        handle_frontend_infraestructure()
    
    if '--backend' in args:
        handle_backend_infraestructrue()
    
    if '--frontend' not in args and '--backend' not in args:
        run_all = str(input('Want to create entire infraestructure?(y/N)'))
        if run_all == 'y' or run_all == 'y':
            handle_frontend_infraestructure()
            handle_backend_infraestructrue()
