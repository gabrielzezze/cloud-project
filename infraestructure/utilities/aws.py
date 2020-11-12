import boto3
import os
from utilities.aws_resources.ec2 import create_ec2_instance
import constants.aws as aws_contants


def init_aws_client(type: str, region: str):

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    client = boto3.client(
        type,
        region_name=region,
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    )
    return client


def handle_security_group_creation(aws_client, type):

    # if type == 'frontend':
    #     ec2_client = boto3.resource('ec2', region_name='us-east-1')
    #     sg_name = aws_contants.get_frontend_security_group_name()
        
    #     security_group = create_security_group(ec2_client, sg_name, 'FrontEnd Security Group')
    #     security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
    #     security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=8080, ToPort=8080)

    #     return security_group.id
    
    if type == 'backend':
        ec2_client = boto3.resource('ec2', region_name='us-east-2')
        sg_name = aws_contants.get_backend_security_group_name()

        security_group = create_security_group(ec2_client, sg_name, 'Backend Security Group')
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22)
        security_group.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=5000, ToPort=5000)
        
        return security_group.id


def handle_ec2_instance_creation(aws_client, name, sg_id, type):
    if type == 'frontend':
        ec2_client = boto3.resource('ec2', region_name='us-east-1')

        image_id = aws_contants.get_frontend_image_id()

        instance_id = create_ec2_instance(ec2_client, name, sg_id, image_id, type)
        return instance_id
    
    elif type == 'backend':
        ec2_client = boto3.resource('ec2', region_name='us-east-2')
        
        image_id = aws_contants.get_backend_image_id()
        instance_id = create_ec2_instance(ec2_client, name, sg_id, image_id, type)
        return instance_id


# def handle_launch_configuration_creation(as_client, name, sg_id, type):
#     if type == 'frontend':
#         image_id = aws_contants.get_frontend_image_id()
#         key_name = 'zezze_key'
#         security_groups_ids = [sg_id]

#         create_launch_configuration(
#             as_client,
#             name,
#             image_id,
#             key_name,
#             security_groups_ids
#         )


# def handle_auto_scaling_group_creation(as_client, name, target_groups_arns, subnets_ids, type):
#     if type == 'frontend':
#         launch_config_name = aws_contants.get_frontend_launch_config_name()

#         create_auto_scaling_group(
#             as_client,
#             name,
#             launch_config_name,
#             target_groups_arns,
#             2,
#             subnets_ids,
#             type
#         )


# def handle_load_balancer_creation(elb_client, name, subnets, sg_id, type):
#     if type == 'frontend':
#         lb_arn = create_load_balancer_instance(
#             elb_client, 
#             name, 
#             subnets, 
#             sg_id
#         )
#         return lb_arn
        

# def handle_target_group_creation(elb_client, name, vpc_id, type):
#     if type == 'frontend':
#         tg_arn = create_target_group(
#             elb_client,
#             name,
#             'HTTP',
#             8080,
#             vpc_id
#         )

#         return tg_arn


# def handle_listener_creation(elb_client, tg_arn, lb_arn, type):
#     if type == 'frontend':
#         default_actions = [
#             {
#                 'TargetGroupArn': tg_arn,
#                 'Type': 'forward',
#             }
#         ]
        
#         listener = create_listener(
#             elb_client,
#             default_actions,
#             lb_arn,
#             8080,
#             'HTTP'
#         )
#         return listener
