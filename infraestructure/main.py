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
    res = nv_aws_client.describe_route_tables(
        Filters=[
            {
                'Name': 'association.subnet-id',
                'Values': [
                    frontend_public_subnet.id
                ]
            }
        ]
    )
    route_table_id = res.get('RouteTables', [{}])[0].get('RouteTableId', None)
    if route_table_id:
        frontend_public_route_table = nv_ec2_client.RouteTable(route_table_id)
        frontend_public_route_table.create_route(
            DestinationCidrBlock='14.0.0.0/16', 
            NetworkInterfaceId=frontend_outway.network_interface_id
        )

    # Database
    database = Database(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    database()

    # Application
    application = Backend(ohio_aws_client, ohio_ec2_client, vpc_id, private_subnet, public_subnet)
    application(database.PRIVATE_IP_ADDRESS)


    # Frontend Application
    frontend_outway.elastic_ip.get_ip()
    frontend = Frontend(nv_aws_client, nv_ec2_client, nv_elb_client, nv_as_client, ohio_aws_client, frontend_vpc_obj, frontend_public_subnet, frontend_private_subnet)
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
