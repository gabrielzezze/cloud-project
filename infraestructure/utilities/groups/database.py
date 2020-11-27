from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.aws_resources.security_group import SecurityGroup
from utilities.vpn.keys import Keys
import os
from constants.aws import (
    get_database_security_group_name,
    get_backend_elastic_ip_name,
    get_database_image_id,
    get_database_elastic_ip_name,
    get_backend_vpn_gateway_elastic_ip_name
)

class Database():
    def __init__(self,  aws_client, ec2_client, vpc, private_subnet, public_subnet):
        self.ec2_client = ec2_client
        self.aws_client = aws_client

        self.vpc = vpc
        self.private_subnet = private_subnet
        self.public_subnet = public_subnet

        self.PRIVATE_IP_ADDRESS = '14.0.1.30'

        self.ec2 = None
        self.security_group = None
        self.DATABASE_MACHINE_NAME = "zezze-mysql-database"
        self.USER_DATA_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/aws/database/user_data.sh'
        )

        self._prepare_resources()
        self.keys()

    def _prepare_resources(self):
        # EC2 Resource
        self.ec2 = EC2(self.ec2_client, self.DATABASE_MACHINE_NAME, 'database', subnet_id=self.private_subnet.id, private_ip_address=self.PRIVATE_IP_ADDRESS)

        # Database Resource
        security_group_name = get_database_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, security_group_name, self.vpc.id)

        # Backend Elastic Ip
        # backend_elastic_ip_name = get_backend_elastic_ip_name()
        # self.backend_elastic_ip = ElasticIP(self.aws_client, backend_elastic_ip_name)

        # Elastic Ip
        # database_elastic_ip_name = get_database_elastic_ip_name()
        # self.elastic_ip = ElasticIP(self.aws_client, database_elastic_ip_name)
        
        # Gateway Elastic IP
        gateway_elastic_ip_name = get_backend_vpn_gateway_elastic_ip_name()
        self.gateway_elastic_ip = ElasticIP(self.aws_client, gateway_elastic_ip_name)

        # VPN Keys
        self.keys = Keys()
        


    def _destroy_previous_env(self):
        # Waiter
        instance_terminated_waiter = self.aws_client.get_waiter('instance_terminated')

        # Delete DB instance
        deleted_db_instances = self.ec2.delete_by_group()
        if len(deleted_db_instances) > 0:
            instance_terminated_waiter.wait(InstanceIds=deleted_db_instances)
        
        # Delete security group
        sgs = self.vpc.security_groups.filter(Filters=[{ "Name": "group-name", 'Values': [self.security_group.name] }])
        sgs = list(sgs.all())
        if len(sgs) > 0:
            self.security_group.delete(sg_id=sgs[0].id)


    def _handle_security_group(self):
        security_group = self.security_group.create('Database security group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp=self.private_subnet.cidr_block, FromPort=80, ToPort=80)
        
    def _handle_ec2_instance(self):
        image_id = get_database_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        self.gateway_elastic_ip.get_ip()
        if self.gateway_elastic_ip.ip is None:
            print('[INFO] Gateway elastic ip not found, creating one now ...')
            self.gateway_elastic_ip.create()

        if user_data_script is not None:
            user_data_script = user_data_script.replace('$MYSQL_ROOT_PASSWORD', f"'{os.getenv('MYSQL_ROOT_PASSWORD')}'")
            self.ec2.create(self.security_group.id, image_id, user_data_script)
        else:
            print('[ Error ] Unable to read user data')

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
    

    def __call__(self):
        print('__DATABASE__')
        print('Destroy Previuous env...')
        self._destroy_previous_env()

        print('Create security group...')
        self._handle_security_group()

        print('Create EC2 instance...')
        self._handle_ec2_instance()

        print('Waiting Instance ...')
        running_waiter = self.aws_client.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=[self.ec2.id])

        # print('Creating Elastic IP if needed...')
        # self._handle_elastic_ip_creation()
        # print('Allocating Elastic IP...')
        # self._handle_elastic_ip_association()

        print('Done')