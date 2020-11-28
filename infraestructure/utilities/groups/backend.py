from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.aws_resources.security_group import SecurityGroup
from utilities.vpn.keys import Keys
import os
from constants.aws import (
    get_backend_security_group_name, 
    get_elastic_ip_alloc_id, 
    get_backend_image_id,
    get_backend_elastic_ip_name,
    get_database_elastic_ip_name,
    get_backend_vpn_gateway_elastic_ip_name
)

class Backend():
    def __init__(self, aws_client, ec2_client, vpc, private_subnet, public_subnet):
        self.aws_client = aws_client
        self.ec2_client = ec2_client

        self.vpc = vpc
        self.private_subnet = private_subnet
        self.public_subnet = public_subnet

        self.BACKEND_MACHINES_NAMES = [
            'zezze-backend-0'
        ]
        self.USER_DATA_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/aws/backend/user_data.sh'
        )
        self.PRIVATE_IP_ADDRESS = "14.0.1.40"
        self._prepare_resources()
        self.keys()

    def _prepare_resources(self):
        # EC2
        self.ec2 = EC2(self.ec2_client, self.BACKEND_MACHINES_NAMES[0], 'backend', subnet_id=self.private_subnet.id, private_ip_address=self.PRIVATE_IP_ADDRESS)

        # Security Group
        security_group_name = get_backend_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, security_group_name, self.vpc.id)

        # Gateway Elastic IP
        gateway_elastic_ip_name = get_backend_vpn_gateway_elastic_ip_name()
        self.gateway_elastic_ip = ElasticIP(self.aws_client, gateway_elastic_ip_name)

        # Vpn Keys
        self.keys = Keys()


    def _destroy_previous_env(self):
        # Waiters
        termination_waiter = self.aws_client.get_waiter('instance_terminated')

        # Delete EC2 instances
        deleted_instances_ids = self.ec2.delete_by_group()
        if len(deleted_instances_ids) > 0:
            termination_waiter.wait(InstanceIds=deleted_instances_ids)
        
        # Delete security group
        sgs = self.vpc.security_groups.filter(Filters=[{ "Name": "group-name", 'Values': [self.security_group.name] }])
        sgs = list(sgs.all())
        if len(sgs) > 0:
            self.security_group.delete(sg_id=sgs[0].id)


    def _handle_security_group(self):
        security_group = self.security_group.create('Backend Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp=self.public_subnet.cidr_block, FromPort=5000, ToPort=5000)


    def _handle_ec2_instance(self, database_vpn_address):
        image_id = get_backend_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        if user_data_script is not None:
            user_data_script = user_data_script.replace('$DATABASE_IP', database_vpn_address)
            user_data_script = user_data_script.replace('$DATABASE_PASSWORD', f"{os.getenv('MYSQL_ROOT_PASSWORD')}")
            self.ec2.create(self.security_group.id, image_id, user_data_script)

            network_interfaces = self.ec2_client.network_interfaces.filter(
                Filters=[{ 'Name': 'group-id', 'Values': [self.security_group.id] }]
            )
            network_interfaces = list(network_interfaces)
            if len(network_interfaces) > 0:
                network_interfaces[0].modify_attribute(SourceDestCheck={ 'Value': False })


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

    def __call__(self, database_vpn_address):
        print('__BACKEND APPLICATION__')
        print('Destroing previous env...')
        self._destroy_previous_env()

        print('Create Security Group...')
        self._handle_security_group()

        print('Creating EC2 insances...')
        self._handle_ec2_instance(
            database_vpn_address=database_vpn_address
        )
        
        print('Waiting for instances...')
        running_waiter = self.aws_client.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=[self.ec2.id])
        
        # print('Creating Elastic IP if needed...')
        # self._handle_elastic_ip_creation()
        # print('Allocating Elastic IP...')
        # self._handle_elastic_ip_association()

        print('Done :) \n')

