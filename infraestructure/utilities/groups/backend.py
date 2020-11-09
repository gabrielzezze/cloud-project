from ..aws import handle_ec2_instance_creation, handle_security_group_creation
from utilities.aws_resources.ec2 import delete_ec2_instances_by_group
from utilities.aws_resources.security_group import delete_security_group_by_name
from constants.aws import get_backend_security_group_name

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
    

    def __call__(self):
        print('Destroing previous env...')
        self._destroy_previous_env()

        print('Create Security Group...')
        self._handle_security_group()

        print('Creating EC2 insances...')
        self._handle_ec2_instance()

