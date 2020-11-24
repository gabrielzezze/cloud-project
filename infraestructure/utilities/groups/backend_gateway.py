from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.security_group import SecurityGroup
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.vpn.keys import Keys
import os
import subprocess
from constants.aws import (
    get_backend_vpn_gateway_name,
    get_backend_vpn_gateway_security_group_name,
    get_backend_vpn_gateway_image_id,
    get_backend_vpn_gateway_elastic_ip_name
)

class BackendGateway():
    def __init__(self, aws_client, ec2_client):
        self.aws_client = aws_client
        self.ec2_client = ec2_client

        self.USER_DATA_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/aws/backend_gateway/user_data.sh'
        )

        self._prepare_resources()
        self.keys()


    def _prepare_resources(self):
        name = get_backend_vpn_gateway_name()
        self.ec2 = EC2(self.ec2_client, name, 'backend-gateway')

        sg_name = get_backend_vpn_gateway_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, sg_name)

        # Elastic IP
        elastic_ip_name = get_backend_vpn_gateway_elastic_ip_name()
        self.elastic_ip = ElasticIP(self.aws_client, elastic_ip_name)

        # VPN Keys
        self.keys = Keys()


    def _destroy_previous_env(self):
        termination_waiter = self.aws_client.get_waiter('instance_terminated')

        # Delete EC2 instances
        deleted_instances_ids = self.ec2.delete_by_group()
        if len(deleted_instances_ids) > 0:
            termination_waiter.wait(InstanceIds=deleted_instances_ids)
        
        # Delete security group
        self.security_group.delete()


    def _handle_security_group(self):
        security_group = self.security_group.create('Backend VPN Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=5000, ToPort=5000)
        security_group.authorize_ingress(IpProtocol="udp", CidrIp="0.0.0.0/0", FromPort=51820, ToPort=51820)

    def _handle_ec2_instances(self, application_keys, database_keys):
        image_id = get_backend_vpn_gateway_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        if user_data_script is not None:
            user_data_script = user_data_script.replace('$SERVER_PRIVATE_KEY', self.keys.private_key)
            user_data_script = user_data_script.replace('$APPLICATION_PUBLIC_KEY', application_keys.public_key)
            user_data_script = user_data_script.replace('$DATABASE_PUBLIC_KEY', database_keys.public_key)
            self.ec2.create(self.security_group.id, image_id, user_data=user_data_script)

    def _handle_elastic_ip_association(self):
        instance_id = self.ec2.id

        if instance_id is not None:
            self.aws_client.associate_address(
                InstanceId   = instance_id,
                AllocationId = self.elastic_ip.allocation_id
            )
    
    def _handle_elastic_ip_creation(self):
        self.elastic_ip.get_ip()

        if (self.elastic_ip.ip is None or self.elastic_ip.allocation_id is None):
            self.elastic_ip.create()


    def __call__(self, application_keys, database_keys):
        print('__BACKEND GATEWAY__')

        print('Cleaning previous env...')
        self._destroy_previous_env()

        print('Creating new security group...')
        self._handle_security_group()

        print('Creating ec2 instance...')
        self._handle_ec2_instances(
            application_keys=application_keys, 
            database_keys=database_keys
        )

        print('Waiting for instances to be available...')
        running_waiter = self.aws_client.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=[self.ec2.id])

        print('Creating Elastic IP if needed...')
        self._handle_elastic_ip_creation()
        print('Allocating Elastic IP...')
        self._handle_elastic_ip_association()

        print('Done :) \n')