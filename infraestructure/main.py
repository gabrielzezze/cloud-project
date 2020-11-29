from utilities.aws import init_aws_client
from utilities.groups.frontend import Frontend
from utilities.groups.frontend_outway import FrontendOutway
from utilities.groups.backend import Backend
from utilities.groups.database import Database
from utilities.groups.backend_gateway import BackendGateway
from utilities.groups.backend_vpc import BackendVPC
import os
import boto3
import sys

def handle_frontend_infraestructure():
    aws_client  = init_aws_client('ec2', 'us-east-1')
    ec2_client  = boto3.resource('ec2', region_name='us-east-1')
    elb_client  = init_aws_client('elbv2', 'us-east-1')
    as_client   = init_aws_client('autoscaling', 'us-east-1')
    ohio_aws_client = init_aws_client('ec2', 'us-east-2')

    frontend = Frontend(aws_client, ec2_client, elb_client, as_client, ohio_aws_client)
    frontend()

def handle_backend_infraestructrue():
    aws_client = init_aws_client('ec2', 'us-east-2')
    ec2_client = boto3.resource('ec2', region_name='us-east-2')

    vpc = BackendVPC(aws_client, ec2_client)
    vpc_id, private_subnet, public_subnet = vpc()

    backend_gateway = BackendGateway(aws_client, ec2_client, vpc_id, private_subnet, public_subnet)
    database = Database(aws_client, ec2_client, vpc_id, private_subnet, public_subnet)
    application = Backend(aws_client, ec2_client, vpc_id, private_subnet, public_subnet)

    backend_gateway()
    # database()
    # application(database.PRIVATE_IP_ADDRESS)


def main():
    print('INIT INFRAESTRUCTURE')
    print('################################### \n')
    # Frontend Clients
    nv_aws_client  = init_aws_client('ec2', 'us-east-1')
    nv_ec2_client  = boto3.resource('ec2', region_name='us-east-1')
    nv_elb_client  = init_aws_client('elbv2', 'us-east-1')
    nv_as_client   = init_aws_client('autoscaling', 'us-east-1')

    # Backend Clients
    ohio_aws_client = init_aws_client('ec2', 'us-east-2')
    ohio_ec2_client = boto3.resource('ec2', region_name='us-east-2')
    
    # Backend VPC
    vpc = BackendVPC(ohio_aws_client, ohio_ec2_client)
    vpc_id, private_subnet, public_subnet = vpc()

    # Frontend Outway
    frontend_outway = FrontendOutway(nv_aws_client, nv_ec2_client)

    # Backend Gateway
    backend_gateway = BackendGateway(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    backend_gateway(frontend_outway.keys, frontend_outway.VPN_ADDRESS)

    # Creating Frontend Outway
    frontend_outway(backend_gateway.keys, f'{backend_gateway.elastic_ip.ip}:51820')

    # # Database
    # database = Database(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    # database()

    # # Application
    # application = Backend(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    # application(database.PRIVATE_IP_ADDRESS)

    # Frontend Application
    frontend = Frontend(nv_aws_client, nv_ec2_client, nv_elb_client, nv_as_client, ohio_aws_client)
    frontend(frontend_outway.elastic_ip.ip)



if __name__ == '__main__':
    main()
    # args = sys.argv

    # if '--frontend' in args:
    #     handle_frontend_infraestructure()
    
    # if '--backend' in args:
    #     handle_backend_infraestructrue()

    # if '--frontend' not in args and '--backend' not in args:
    #     run_all = str(input('Want to create entire infraestructure?(y/N)'))
    #     if run_all == 'y' or run_all == 'y':
    #         handle_frontend_infraestructure()
    #         handle_backend_infraestructrue()
