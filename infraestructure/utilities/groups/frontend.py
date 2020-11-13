from utilities.aws_resources.load_balancer import LoadBalancer
from utilities.aws_resources.target_group import TargetGroup
from utilities.aws_resources.listener import Listener
from utilities.aws_resources.security_group import SecurityGroup
from utilities.aws_resources.launch_configuration import LaunchConfiguration
from utilities.aws_resources.auto_scaling_group import AutoScalingGroup
from constants.aws import (
    get_frontend_load_balancer_name, 
    get_frontend_lb_target_group_name, 
    get_frontend_security_group_name, 
    get_frontend_auto_scaling_group_name, 
    get_frontend_launch_config_name, 
    get_frontend_image_id
)

class Frontend():
    def __init__(self, aws_client, ec2_client, elb_client, as_client):
        self.aws_client = aws_client
        self.ec2_client = ec2_client
        self.elb_client = elb_client
        self.as_client  = as_client

        self._prepare_resources()
    

    def _prepare_resources(self):
        as_group_name = get_frontend_auto_scaling_group_name()
        self.auto_scaling_group = AutoScalingGroup(self.as_client, as_group_name, 'frontend')

        sg_group_name = get_frontend_security_group_name()
        self.security_group = SecurityGroup(self.aws_client, self.ec2_client, sg_group_name)

        lb_name = get_frontend_load_balancer_name()
        self.load_balancer = LoadBalancer(self.elb_client, lb_name)

        tg_name = get_frontend_lb_target_group_name()
        self.target_group = TargetGroup(self.elb_client, tg_name, 'frontend')
    
        self.listener = Listener(self.elb_client, None)

        launch_config_name = get_frontend_launch_config_name()
        self.launch_configuration = LaunchConfiguration(self.as_client, launch_config_name)


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
        self.security_group.delete()


    def _handle_frontend_security_group(self):
        security_group = self.security_group.create('Frontend Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=8080, ToPort=8080) 


    def _handle_frontend_load_balancer(self):
        running_waiter = self.aws_client.get_waiter('instance_running')

        subnets = [subnet.id for subnet in list(self.ec2_client.subnets.all())]
        self.load_balancer.create(subnets, self.security_group.id)

        vpc_id = list(self.ec2_client.vpcs.all())[0].id
        self.target_group.create('HTTP', 8080, vpc_id)

        default_actions = [{
                'TargetGroupArn': self.target_group.arn,
                'Type': 'forward'
            }]
        self.listener.load_balancer_arn = self.load_balancer.arn
        self.listener.create(default_actions, 8080, 'HTTP')


    def _handle_frontend_launch_configuration(self):
        image_id = get_frontend_image_id()
        self.launch_configuration.create(image_id, 'zezze_key', [self.security_group.id])


    def _handle_frontend_auto_scaling_group(self):
        subnets = ','.join([subnet.id for subnet in list(self.ec2_client.subnets.all())])
        self.auto_scaling_group.create(self.launch_configuration.name, [self.target_group.arn], 2, subnets)


    def __call__(self):
        print('Init Fronend Deploy')

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




    