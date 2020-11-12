class Listener():
    def __init__(self, elb_client, load_balancer_arn):
        self.elb_client = elb_client
        self.load_balancer_arn = load_balancer_arn
        self.arn = None


    def _get_arn_by_load_balancer_arn(self):
        listeners = self.elb_client.describe_listeners(LoadBalancerArn=self.load_balancer_arn)
        listeners = listeners.get('Listeners', [])
        if len(listeners) > 0:
            self.arn = listeners[0].get('ListenerArn', None)

    def delete(self):
        self._get_arn_by_load_balancer_arn()
        if self.arn is not None:
            response = self.elb_client.delete_listener(
                ListenerArn=self.arn
            )

    def create(self, default_actions, port, protocol):
        listener = self.elb_client.create_listener(
            DefaultActions=default_actions,
            LoadBalancerArn=self.load_balancer_arn,
            Port=port,
            Protocol=protocol
        )

        return listener
