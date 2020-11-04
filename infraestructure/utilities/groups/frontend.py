from ..aws import handle_ec2_instance_creation, handle_security_group_creation, handle_load_balancer_creation, handle_target_group_creation, handle_listener_creation
from utilities.aws_resources.ec2 import delete_ec2_instances_by_group
from utilities.aws_resources.load_balancer import delete_load_balancer_by_name, _get_load_balancer_arn_by_name
from utilities.aws_resources.target_group import delete_target_group_by_name
from utilities.aws_resources.listener import delete_listener_by_load_balancer_arn
from utilities.aws_resources.security_group import delete_security_group_by_name
from constants.aws import get_frontend_load_balancer_name, get_frontend_lb_target_group_name, get_frontend_security_group_name

class Frontend():
    def __init__(self, aws_client, ec2_client, elb_client):
        self.aws_client = aws_client
        self.ec2_client = ec2_client
        self.elb_client = elb_client

        self.FRONTEND_MACHINES_NAMES = [
            'zezze-frontend-0',
            'zezze-frontend-1'
        ]
    
    def _destroy_previous_env(self):

        load_balancer_deleted_waiter = self.elb_client.get_waiter('load_balancers_deleted')
        termination_waiter = self.aws_client.get_waiter('instance_terminated')

        name = get_frontend_load_balancer_name()
        lb_arn = _get_load_balancer_arn_by_name(self.elb_client, name)
        if lb_arn is not None:
            # Delete previous listener
            delete_listener_by_load_balancer_arn(self.elb_client, lb_arn)
        
            # Delete load balancer
            delete_load_balancer_by_name(self.elb_client, name)
            load_balancer_deleted_waiter.wait(LoadBalancerArns=[lb_arn])

            # Delete target group
            tg_name = get_frontend_lb_target_group_name()
            delete_target_group_by_name(self.elb_client, tg_name)

        # Delete EC2 frontend instances
        deleted_instances_ids = delete_ec2_instances_by_group(self.ec2_client, 'frontend')
        if len(deleted_instances_ids) != 0:
            termination_waiter.wait(InstanceIds=deleted_instances_ids)


    def _handle_frontend_security_group(self):
        name = get_frontend_security_group_name()
        delete_security_group_by_name(self.aws_client, name)
        sg_id = handle_security_group_creation(self.aws_client, 'frontend')
        self.security_group_id = sg_id

    def _handle_frontend_ec2_instances(self):

        instances_ids = []
        for machine_name in self.FRONTEND_MACHINES_NAMES:
            instance_id = handle_ec2_instance_creation(self.aws_client, machine_name, self.security_group_id, 'frontend')
            instances_ids.append({ 'Id': instance_id })
        
        self.ec2_instances = instances_ids
    
    def _handle_frontend_load_balancer(self):
        running_waiter = self.aws_client.get_waiter('instance_running')

        name = get_frontend_load_balancer_name()

        subnets = [subnet.id for subnet in list(self.ec2_client.subnets.all())]
        lb_arn = handle_load_balancer_creation(
            self.elb_client,
            name,
            subnets,
            self.security_group_id,
            'frontend'
        )

        vpc_id = list(self.ec2_client.vpcs.all())[0].id
        tg_name = get_frontend_lb_target_group_name()
        tg_arn = handle_target_group_creation(
            self.elb_client,
            tg_name,
            vpc_id,
            'frontend'
        )

        _listener = handle_listener_creation(
            self.elb_client, 
            tg_arn, 
            lb_arn, 
            'frontend'
        )

        running_waiter.wait(InstanceIds=[instance.get('Id', None) for instance in self.ec2_instances])

        rg_targets = self.elb_client.register_targets(
            TargetGroupArn=tg_arn,
            Targets=self.ec2_instances
        )

        self.load_balancer_arn = lb_arn

    def __call__(self):
        print('Init Fronend Deploy')

        self._destroy_previous_env()

        print('Security group...')
        self._handle_frontend_security_group()
        print('EC2 instances...')
        self._handle_frontend_ec2_instances()
        print('Load balancer...')
        self._handle_frontend_load_balancer()
        print('Done')


        lb = self.elb_client.describe_load_balancers(LoadBalancerArns=[self.load_balancer_arn])
        addr = lb.get('LoadBalancers', [{}])[0].get('DNSName', None)
        print(f'Frontend Available at: {addr}')




    