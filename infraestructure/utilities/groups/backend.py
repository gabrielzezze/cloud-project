from ..aws import handle_ec2_instance_creation, handle_security_group_creation
from utilities.aws_resources.ec2 import delete_ec2_instances_by_group
from utilities.aws_resources.security_group import delete_security_group_by_name
from constants.aws import get_backend_security_group_name, get_elastic_ip_alloc_id

class Backend():
    def __init__(self, aws_client, ec2_client):
        self.aws_client = aws_client
        self.ec2_client = ec2_client

        self.BACKEND_MACHINES_NAMES = [
            'zezze-backend-0'
        ]

    
    def _destroy_previous_env(self):
        # Waiters
        termination_waiter = self.aws_client.get_waiter('instance_terminated')

        # Delete EC2 instances
        deleted_instances_ids = delete_ec2_instances_by_group(self.ec2_client, 'backend')
        if len(deleted_instances_ids) > 0:
            termination_waiter.wait(InstanceIds=deleted_instances_ids)
        
        # Delete security group
        name = get_backend_security_group_name()
        delete_security_group_by_name(self.aws_client, name)
    

    def _handle_security_group(self):
        sg_id = handle_security_group_creation(self.aws_client, 'backend')
        self.security_group_id = sg_id
    
    def _handle_ec2_instance(self):
        instances_ids = []
        name = self.BACKEND_MACHINES_NAMES[0]

        instance_id = handle_ec2_instance_creation(self.aws_client, name, self.security_group_id, 'backend')
        instances_ids.append({ 'Id': instance_id })

        self.ec2_instances = instances_ids
    
    def _handle_elastic_ip_association(self):
        instance_id = self.ec2_instances[0].get('Id', None)
        allocation_id = get_elastic_ip_alloc_id()
        if instance_id is not None:
            self.aws_client.associate_address(
                InstanceId   = instance_id,
                AllocationId = "eipalloc-0383a09bbaf5d3687"
            )
    
    def _handler_auto_scalling(self):
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
        running_waiter.wait(InstanceIds=[instance.get('Id', None) for instance in self.ec2_instances])
        
        print('Association Elastic IP...')
        self._handle_elastic_ip_association()

