from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.security_group import SecurityGroup
from constants.aws import (
    get_backend_security_group_name, 
    get_elastic_ip_alloc_id, 
    get_backend_image_id
)

class Backend():
    def __init__(self, aws_client, ec2_client):
        self.aws_client = aws_client
        self.ec2_client = ec2_client

        self.BACKEND_MACHINES_NAMES = [
            'zezze-backend-0'
        ]

        self._prepare_resources()

    def _prepare_resources(self):
        self.ec2 = EC2(self.ec2_client, self.BACKEND_MACHINES_NAMES[0], 'backend')

        security_group_name = get_backend_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, security_group_name)


    def _destroy_previous_env(self):
        # Waiters
        termination_waiter = self.aws_client.get_waiter('instance_terminated')

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
        self.ec2.create(self.security_group.id, image_id)


    def _handle_elastic_ip_association(self):
        instance_id = self.ec2.id
        allocation_id = get_elastic_ip_alloc_id()

        if instance_id is not None:
            self.aws_client.associate_address(
                InstanceId   = instance_id,
                AllocationId = allocation_id
            )
    
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
        
        print('Association Elastic IP...')
        self._handle_elastic_ip_association()
