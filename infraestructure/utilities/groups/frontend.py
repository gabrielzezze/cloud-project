from utilities.aws_resources.load_balancer import LoadBalancer
from utilities.aws_resources.target_group import TargetGroup
from utilities.aws_resources.listener import Listener
from utilities.aws_resources.security_group import SecurityGroup
from utilities.aws_resources.launch_configuration import LaunchConfiguration
from utilities.aws_resources.auto_scaling_group import AutoScalingGroup
from utilities.aws_resources.elastic_ip import ElasticIP
from utilities.aws_resources.vpc.subnet import Subnet
from constants.aws import (
    get_frontend_load_balancer_name, 
    get_frontend_lb_target_group_name, 
    get_frontend_security_group_name, 
    get_frontend_auto_scaling_group_name, 
    get_frontend_launch_config_name, 
    get_frontend_image_id,
    get_backend_elastic_ip_name
)
import os
import time

class Frontend():
    def __init__(self, aws_client, ec2_client, elb_client, as_client, ohio_aws_client, vpc, public_subnet, private_subnet):
        self.aws_client = aws_client
        self.ec2_client = ec2_client
        self.elb_client = elb_client
        self.as_client  = as_client
        self.ohio_aws_client = ohio_aws_client

        self.vpc = vpc
        self.public_subnet = public_subnet
        self.private_subnet = private_subnet

        self.USER_DATA_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/aws/frontend/user_data.sh'
        )

        self._prepare_resources()
    

    def _prepare_resources(self):
        as_group_name = get_frontend_auto_scaling_group_name()
        self.auto_scaling_group = AutoScalingGroup(self.as_client, as_group_name, 'frontend')

        sg_group_name = get_frontend_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, sg_group_name, self.vpc.id)

        lb_name = get_frontend_load_balancer_name()
        self.load_balancer = LoadBalancer(self.elb_client, lb_name)

        tg_name = get_frontend_lb_target_group_name()
        self.target_group = TargetGroup(self.elb_client, tg_name, 'frontend')
    
        self.listener = Listener(self.elb_client, None)

        launch_config_name = get_frontend_launch_config_name()
        self.launch_configuration = LaunchConfiguration(self.as_client, launch_config_name)

        backend_elastic_ip_name = get_backend_elastic_ip_name()
        self.backend_elastic_ip = ElasticIP(self.ohio_aws_client, backend_elastic_ip_name)


    def _destroy_previous_env(self):
        load_balancer_deleted_waiter = self.elb_client.get_waiter('load_balancers_deleted')
        termination_waiter = self.aws_client.get_waiter('instance_terminated')

        is_deleting_previous_as_group = self.auto_scaling_group.delete()
        self.launch_configuration.delete()
        
        self.load_balancer._get_arn_by_name()

        if self.load_balancer.arn is not None:
            # Delete previous listener
            self.listener.load_balancer_arn = self.load_balancer.arn
            self.listener.delete()
        
            # Delete load balancer
            deleting_load_balancer = self.load_balancer.delete()
            if deleting_load_balancer:
                load_balancer_deleted_waiter.wait(Names=[self.load_balancer.name])

            # Delete target group
            self.target_group.delete()

        if is_deleting_previous_as_group:
            termination_waiter.wait(
                Filters=[
                    { 'Name': 'tag:Owner', 'Values': [ 'zezze' ] },
                    { 'Name': 'tag:Type', 'Values':  ['frontend'] }
                ])

        # Delete security group
        sgs = self.vpc.security_groups.filter(Filters=[{ "Name": "group-name", 'Values': [self.security_group.name] }])
        sgs = list(sgs.all())
        if len(sgs) > 0:
            self.security_group.delete(sg_id=sgs[0].id)
            


    def _handle_frontend_security_group(self):
        security_group = self.security_group.create('Frontend Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=80, ToPort=80)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=443, ToPort=443)


    def _handle_frontend_load_balancer(self):
        running_waiter = self.aws_client.get_waiter('instance_running')

        subnets = [self.public_subnet.id, self.second_public_subnet.id]
        self.load_balancer.create(subnets, self.security_group.id)

        self.target_group.create('HTTP', 80, self.vpc.id)

        default_actions = [{
                'TargetGroupArn': self.target_group.arn,
                'Type': 'forward'
            }]
        self.listener.load_balancer_arn = self.load_balancer.arn
        self.listener.create(default_actions, 80, 'HTTP')


    def _handle_frontend_launch_configuration(self):
        image_id = get_frontend_image_id()

        user_data_script = None
        with open(self.USER_DATA_SCRIPT_PATH, 'r') as script_file:
            user_data_script = '\n'.join(script_file)

        if user_data_script is not None:
            self.launch_configuration.create(image_id, 'zezze_key', [self.security_group.id], user_data=user_data_script, instance_type='t2.small')


    def _handle_frontend_auto_scaling_group(self):
        subnets = f'{self.public_subnet.id},{self.second_public_subnet.id}'
        self.auto_scaling_group.create(self.launch_configuration.name, [self.target_group.arn], 2, subnets)


    def __call__(self):
        print('Init Fronend Deploy')

        print('Destroing Env...')
        self._destroy_previous_env()

        print('Security group...')
        self._handle_frontend_security_group()

        print('Load balancer...')
        self._handle_frontend_load_balancer()

        print('Creating Launch config...')
        self._handle_frontend_launch_configuration()

        print('Waiting for load balancer availability...')
        load_balancer_availability_waiter = self.elb_client.get_waiter('load_balancer_available')
        load_balancer_availability_waiter.wait(LoadBalancerArns=[self.load_balancer.arn])

        print('Creating auto scaling group...')
        self._handle_frontend_auto_scaling_group()

        print('Done')




    