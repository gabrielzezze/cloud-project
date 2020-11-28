import os
from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.security_group import SecurityGroup
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.vpn.keys import Keys
from constants.aws import (
    get_frontend_outway_name,
    get_frontend_outway_security_group_name,
    get_frontend_outway_image_id
)

class FrontendOutway():
    def __init__(self, ec2_client, ec2_resource):
        self.ec2_client = ec2_client
        self.ec2_resource = ec2_resource
        self.name = get_frontend_outway_name()

        self.USER_DATA_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/aws/frontend_outway/user_data.sh'
        )
        self._prepare_resources()
        self.keys()

    def _prepare_resources(self):
        self.ec2 = EC2(self.ec2_resource, self.name, 'frontend-gateway')

        sg_name = get_frontend_outway_security_group_name()
        self.security_group = SecurityGroup(self.ec2_client, self.ec2_resource, sg_name)

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
        security_group = self.security_group.create('Frontend Outway Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=80, ToPort=80)
        security_group.authorize_ingress(IpProtocol="udp", CidrIp="0.0.0.0/0", FromPort=51820, ToPort=51820)

    def _handle_ec2_instances(self):
        image_id = get_frontend_outway_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        if user_data_script is not None:
            user_data_script = user_data_script.replace('$SERVER_PRIVATE_KEY', self.keys.private_key)
            self.ec2.create(self.security_group.id, image_id, user_data=user_data_script)