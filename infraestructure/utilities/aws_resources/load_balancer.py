import time
def _get_load_balancer_arn_by_name(elb_client, name):
    try:
        lbs = elb_client.describe_load_balancers(
            Names=[name]
        )
        return lbs.get('LoadBalancers', [{}])[0].get('LoadBalancerArn', None)
    except Exception as e:
        print('Delet LB: ', e)
        return None

def delete_load_balancer_by_name(elb_client, name):
    lb_arn = _get_load_balancer_arn_by_name(elb_client, name)
    if lb_arn is None:
        return None

    res = elb_client.delete_load_balancer(
        LoadBalancerArn=lb_arn
    )
    return lb_arn

def create_load_balancer_instance(elb_client, name, subnets, sg_id):
    lb = elb_client.create_load_balancer(
            Name=name, 
            Subnets=subnets,
            Scheme='internet-facing', 
            Type='application',
            SecurityGroups=[sg_id]
    )
    
    return lb.get('LoadBalancers', [{}])[0].get('LoadBalancerArn', None)
    