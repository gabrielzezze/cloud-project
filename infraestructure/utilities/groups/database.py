from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.aws_resources.security_group import SecurityGroup
import os
from constants.aws import (
    get_database_security_group_name,
    get_backend_elastic_ip_name,
    get_database_image_id
)

class Database():
    def __init__(self,  aws_client, ec2_client):
        self.ec2_client = ec2_client
        self.aws_client = aws_client
        self.ec2 = None
        self.security_group = None
        self.DATABASE_MACHINE_NAME = "zezze-mysql-database"

        self._prepare_resources()

    def _prepare_resources(self):
        # EC2 Resource
        self.ec2 = EC2(self.ec2_client, self.DATABASE_MACHINE_NAME, 'DATABASE')

        # Database Resource
        security_group_name = get_database_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, security_group_name)

        # Backend Elastic Ip
        backend_elastic_ip_name = get_backend_elastic_ip_name()
        self.backend_elastic_ip = ElasticIP(self.aws_client, backend_elastic_ip_name)
        


    def _destroy_previous_env(self):
        # Waiter
        instance_terminated_waiter = self.aws_client.get_waiter('instance_terminated')

        # Delete DB instance
        deleted_db_instances = self.ec2.delete_by_group()
        if len(deleted_db_instances) > 0:
            instance_terminated_waiter.wait(InstanceIds=deleted_db_instances)
        
        # Delete security group
        self.security_group.delete()


    def _handle_security_group(self):
        security_group = self.security_group.create('Database security group')
        backend_ip = self.backend_elastic_ip.get_ip()
        # CidrIp=f"{backend_ip}/32"
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=80, ToPort=80)
        
    def _handle_ec2_instance(self):
        image_id = get_database_image_id()
        # {os.getenv("MYSQL_ROOT_PASSWORD")}
        init_user_data = f'''
            git clone https://github.com/gabrielzezze/cloud-project.git         &&    \
            chmod +x ./cloud-project/infraestructure/scripts/aws/database.sh    &&    \
            export MYSQL_ROOT_PASSWORD='{os.getenv("MYSQL_ROOT_PASSWORD")}'     &&    \
            ./cloud-project/infraestructure/scripts/aws/database.sh             
        '''
        self.ec2.create(self.security_group.id, 'ami-0a91cd140a1fc148a', init_user_data)
    
    def __call__(self):
        print('Destroy Previuous env...')
        self._destroy_previous_env()

        print('Create security group...')
        self._handle_security_group()

        print('Create EC2 instance...')
        self._handle_ec2_instance()

        print('Waiting Instance ...')
        running_waiter = self.aws_client.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=[self.ec2.id])

        print('Done')