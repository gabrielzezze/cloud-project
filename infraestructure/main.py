from utilities.aws import init_aws_client
from utilities.groups.frontend import Frontend
from utilities.groups.frontend_outway import FrontendOutway
from utilities.groups.backend import Backend
from utilities.groups.database import Database
from utilities.groups.backend_gateway import BackendGateway
from utilities.groups.backend_vpc import BackendVPC
from utilities.groups.frontend_vpc import FrontendVPC
import os
import boto3
import sys

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

    frontend_vpc = FrontendVPC(nv_aws_client, nv_ec2_client)
    frontend_vpc_obj, frontend_private_subnet, frontend_public_subnet = frontend_vpc()

    # Frontend Outway
    frontend_outway = FrontendOutway(nv_aws_client, nv_ec2_client, frontend_vpc_obj, frontend_public_subnet, frontend_private_subnet)

    #Backend Gateway
    backend_gateway = BackendGateway(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    backend_gateway(frontend_outway.keys, frontend_outway.VPN_ADDRESS)

    # # Creating Frontend Outway
    frontend_outway(backend_gateway.keys, f'{backend_gateway.elastic_ip.ip}:51820')

    # # Create fronend vpc route table
    frontend_vpc.handle_public_route_table(frontend_outway.network_interface_id)
    frontend_vpc.handle_second_public_subnet()
    # Database
    database = Database(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    database()

    # Application
    application = Backend(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    application(database.PRIVATE_IP_ADDRESS)

    # Frontend Application
    frontend = Frontend(nv_aws_client, nv_ec2_client, nv_elb_client, nv_as_client, ohio_aws_client, frontend_vpc_obj, frontend_public_subnet, frontend_private_subnet)
    frontend.second_public_subnet = frontend_vpc.second_public_subnet
    frontend()



if __name__ == '__main__':
    main()

