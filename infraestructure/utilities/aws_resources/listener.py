def _get_listener_arn_by_load_balancer_arn(elb_client, lb_arn):
    listener = elb_client.describe_listeners(LoadBalancerArn=lb_arn)

    return listener.get('Listeners', [{}])[0].get('ListenerArn', None)

def delete_listener_by_load_balancer_arn(elb_client, lb_arn):
    listener_arn = _get_listener_arn_by_load_balancer_arn(elb_client, lb_arn)
    if listener_arn is not None:
        response = elb_client.delete_listener(
            ListenerArn=listener_arn
        )

def create_listener(elb_client, default_actions, lb_arn, port, protocol):
    listener = elb_client.create_listener(
        DefaultActions=default_actions,
        LoadBalancerArn=lb_arn,
        Port=port,
        Protocol=protocol
    )

    return listener
