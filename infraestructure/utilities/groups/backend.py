from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.aws_resources.security_group import SecurityGroup
import os
from constants.aws import (
    get_backend_security_group_name, 
    get_elastic_ip_alloc_id, 
    get_backend_image_id,
    get_backend_elastic_ip_name
)

class Backend():
    def __init__(self, aws_client, ec2_client):
        self.aws_client = aws_client
        self.ec2_client = ec2_client

        self.BACKEND_MACHINES_NAMES = [
            'zezze-backend-0'
        ]
        self.USER_DATA_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/aws/backend/user_data.sh'
        )

        self._prepare_resources()

    def _prepare_resources(self):
        # EC2
        self.ec2 = EC2(self.ec2_client, self.BACKEND_MACHINES_NAMES[0], 'backend')

        # Security Group
        security_group_name = get_backend_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, security_group_name)

        # Elastic IP
        elastic_ip_name = get_backend_elastic_ip_name()
        self.elastic_ip = ElasticIP(self.aws_client, elastic_ip_name)


    def _destroy_previous_env(self):
        # Waiters
        termination_waiter = self.aws_client.get_waiter('instance_terminated')

        # # Delete elastic ip
        # self.elastic_ip.get_ip()
        # self.elastic_ip.delete()

        # Delete EC2 instances
        deleted_instances_ids = self.ec2.delete_by_group()
        if len(deleted_instances_ids) > 0:
            termination_waiter.wait(InstanceIds=deleted_instances_ids)
        
        # Delete security group
        self.security_group.delete()


    def _handle_security_group(self):
        security_group = self.security_group.create('Backend Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=5000, ToPort=5000)
    
    def _handle_ec2_instance(self):
        image_id = get_backend_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        if user_data_script is not None:
            self.ec2.create(self.security_group.id, image_id, user_data_script)
        else:
            print('[ Error ] Failed to open user data script')

    def _handle_elastic_ip_association(self):
        instance_id = self.ec2.id

        if instance_id is not None:
            self.aws_client.associate_address(
                InstanceId   = instance_id,
                AllocationId = self.elastic_ip.allocation_id
            )
    
    def _handle_elastic_ip_creation(self):
        self.elastic_ip.create()

    def _handle_auto_scalling(self):
        pass

    def __call__(self):
        print('Destroing previous env...')
        self._destroy_previous_env()

        print('Create Security Group...')
        self._handle_security_group()

        print('Creating EC2 insances...')
        self._handle_ec2_instance()
        
        print('Waiting for instances...')
        running_waiter = self.aws_client.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=[self.ec2.id])
        
        # print('Association Elastic IP...')
        # self.elastic_ip.create()
        self.elastic_ip.get_ip()
        self._handle_elastic_ip_association()

