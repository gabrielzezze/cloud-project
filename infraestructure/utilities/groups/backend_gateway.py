from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.security_group import SecurityGroup
import os
from constants.aws import (
    get_backend_vpn_gateway_name,
    get_backend_vpn_gateway_security_group_name,
    get_backend_vpn_gateway_image_id
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


    def _prepare_resources(self):
        name = get_backend_vpn_gateway_name()
        self.ec2 = EC2(self.ec2_client, name, 'backend-gateway')

        sg_name = get_backend_vpn_gateway_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, sg_name)


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
    
    def _handle_ec2_instances(self):
        image_id = get_backend_vpn_gateway_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        if user_data_script is not None:
            self.ec2.create(self.security_group.id, image_id)

    def __call__(self):
        print('Backenf Gateway')

        print('Cleaning previous env...')
        self._destroy_previous_env()

        print('Creating new security group...')
        self._handle_security_group()

        print('Creating ec2 instance...')
        self._handle_ec2_instances()

        print('Waiting for instances to be available...')
        running_waiter = self.aws_client.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=[self.ec2.id])

        print('Done :)')