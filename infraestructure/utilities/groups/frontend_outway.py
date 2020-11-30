import os
from utilities.aws_resources.ec2 import EC2
from utilities.aws_resources.security_group import SecurityGroup
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.vpn.keys import Keys
from constants.aws import (
    get_frontend_outway_name,
    get_frontend_outway_security_group_name,
    get_frontend_outway_image_id,
    get_frontend_outway_elastic_ip_name
)

class FrontendOutway():
    def __init__(self, ec2_client, ec2_resource, vpc, public_subnet, private_subnet):
        self.ec2_client = ec2_client
        self.ec2_resource = ec2_resource
        self.name = get_frontend_outway_name()

        self.vpc = vpc
        self.private_subnet = private_subnet
        self.public_subnet = public_subnet

        self.USER_DATA_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/aws/frontend_outway/user_data.sh'
        )
        self.VPN_ADDRESS = '14.6.0.2'
        self._prepare_resources()
        self.keys()

    def _prepare_resources(self):
        self.ec2 = EC2(self.ec2_resource, self.name, 'frontend-gateway', subnet_id=self.public_subnet.id)

        sg_name = get_frontend_outway_security_group_name()
        self.security_group = SecurityGroup(self.ec2_client, self.ec2_resource, sg_name, self.vpc.id)

        # Elastic IP
        # elastic_ip_name = get_frontend_outway_elastic_ip_name()
        # self.elastic_ip = ElasticIP(self.ec2_client, elastic_ip_name)

        # VPN Keys
        self.keys = Keys()

    def _destroy_previous_env(self):
        termination_waiter = self.ec2_client.get_waiter('instance_terminated')

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
        security_group = self.security_group.create('Frontend Outway Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=80, ToPort=80)
        security_group.authorize_ingress(IpProtocol="udp", CidrIp="0.0.0.0/0", FromPort=51820, ToPort=51820)

    def _handle_ec2_instances(self, gateway_keys, gateway_ip):
        image_id = get_frontend_outway_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        if user_data_script is not None:
            user_data_script = user_data_script.replace('$CLIENT_PRIVATE_KEY', self.keys.private_key)
            user_data_script = user_data_script.replace('$CLIENT_VPN_ADDRESS', self.VPN_ADDRESS)
            user_data_script = user_data_script.replace('$SERVER_PUBLIC_KEY', gateway_keys.public_key)
            user_data_script = user_data_script.replace('$BACKEND_GATEWAY_IP', gateway_ip)
            self.ec2.create(self.security_group.id, image_id, user_data=user_data_script)

            network_interfaces = self.ec2_resource.network_interfaces.filter(
                Filters=[{ 'Name': 'group-id', 'Values': [self.security_group.id] }]
            )
            network_interfaces = list(network_interfaces)
            if len(network_interfaces) > 0:
                self.network_interface_id = network_interfaces[0].id
                network_interfaces[0].modify_attribute(SourceDestCheck={ 'Value': False })

    # def _handle_elastic_ip_association(self):
    #     instance_id = self.ec2.id

    #     if instance_id is not None:
    #         self.ec2_client.associate_address(
    #             InstanceId   = instance_id,
    #             AllocationId = self.elastic_ip.allocation_id
    #         )
    
    # def _handle_elastic_ip_creation(self):
    #     self.elastic_ip.get_ip()

    #     if (self.elastic_ip.ip is None or self.elastic_ip.allocation_id is None):
    #         self.elastic_ip.create()



    def __call__(self, gateway_keys, gateway_ip):
        print('__FRONTEND OUTWAY__')

        print('Cleaning previous env...')
        self._destroy_previous_env()

        print('Creating new security group...')
        self._handle_security_group()

        print('Creating ec2 instance...')
        self._handle_ec2_instances(gateway_keys, gateway_ip)

        print('Waiting for instances to be available...')
        running_waiter = self.ec2_client.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=[self.ec2.id])

        # print('Creating Elastic IP if needed...')
        # self._handle_elastic_ip_creation()
        # print('Allocating Elastic IP...')
        # self._handle_elastic_ip_association()

        print('Done :) \n')