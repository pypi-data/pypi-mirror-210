import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# returns the list of elastic load balancers
def list_elb(self, region: str) -> list:
    logger.info(" ---Inside utils :: list_elb()---")
    """Summary

    Returns:
        TYPE: list
    """

    elb_lst = []

    client = self.session.client('elb', region_name=region)
    marker = ''
    while True:
        if marker == '' or marker is None:
            response = client.describe_load_balancers()
        else:
            response = client.describe_load_balancers(
                Marker=marker
            )
        elb_lst.extend(response['LoadBalancerDescriptions'])
        # for lb in response['LoadBalancerDescriptions']:
        #     elb_lst.append(lb['LoadBalancerName'])

        try:
            marker = response['Marker']
            if marker == '':
                break
        except KeyError:
            break

    return elb_lst


def elb_logging_enabled(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside ensure_elb_access_logging_enabled")

    result = True
    failReason = ""
    offenders = []
    control_id = 'Id3.49'

    compliance_type = "ELB logging enabled"
    description = "Checks if the Application Load Balancer and the Classic Load Balancer have logging enabled"
    resource_type = 'Elastic Load Balancer'
    risk_level = 'Medium'

    regions = self.session.get_available_regions('elb')

    for n in regions:
        try:
            elb_lst = list_elb(self, n)
        except ClientError as e:
            logger.warning("Something went wrong with the region {}: {}".format(n, e))
            continue

        client = self.session.client('elb', region_name=n)
        for elb in elb_lst:
            response = client.describe_load_balancer_attributes(
                LoadBalancerName=elb['LoadBalancerName']
            )
            try:
                if not response['AccessLog']['Enabled']:
                    result = False
                    failReason = "Found load balancer with access logging disabled"
                    offenders.append(elb['LoadBalancerName'])
            except KeyError:
                result = False
                failReason = "Found load balancer with access logging disabled"
                offenders.append(elb['LoadBalancerName'])

    return {
        'Result': result,
        'failReason': failReason,
        'resource_type': resource_type,
        'Offenders': offenders,
        'Compliance_type': compliance_type,
        'Description': description,
        'Risk Level': risk_level,
        'ControlId': control_id
    }
