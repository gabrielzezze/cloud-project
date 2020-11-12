import time
class LoadBalancer():
    def __init__(self, elb_client, name):
        self.elb_client = elb_client
        self.arn = None
        self.name = name

    def _get_arn_by_name(self):
        try:
            lbs = self.elb_client.describe_load_balancers(
                Names=[self.name]
            )
            self.arn = lbs.get('LoadBalancers', [{}])[0].get('LoadBalancerArn', None)
        except Exception as e:
            print('[ Error ] Deleting LoadBalancer: ', e)
            self.arn =  None

    def delete(self):
        self._get_arn_by_name()

        if self.arn is not None:
            res = self.elb_client.delete_load_balancer(
                LoadBalancerArn=self.arn
            )
            return True
        return False

    def create(self, subnets, sg_id):
        lb = self.elb_client.create_load_balancer(
                Name=self.name, 
                Subnets=subnets,
                Scheme='internet-facing', 
                Type='application',
                SecurityGroups=[sg_id]
        )

        self.arn = lb.get('LoadBalancers', [{}])[0].get('LoadBalancerArn', None)
    