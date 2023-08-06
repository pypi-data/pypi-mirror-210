import logging

from botocore.exceptions import ClientError

from .elb_logging_enabled import list_elb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# Ensure that your Amazon Classic Load Balancer listeners are using a secure protocol (HTTPS or SSL)
def elb_tls_https_listeners_only(self) -> dict:
    logger.info(" ---Inside elb_tls_https_listeners_only()")
    """Summary

    Returns:
        TYPE: dict
    """

    result = True
    failReason = ""
    offenders = []
    control_id = 'Id3.50'

    compliance_type = "ELB TLS HTTPS listeners only"
    description = "Checks if your Classic Load Balancer is configured with SSL or HTTPS listeners"
    resource_type = 'Elastic Load Balancer'
    risk_level = 'High'

    regions = self.session.get_available_regions('elb')

    for region in regions:
        try:
            elb_lst = list_elb(self, region)
        except ClientError as e:
            logger.warning("Something went wrong with the region {}: {}".format(region, e))
            continue

        for lb in elb_lst:
            flag = True
            if len(lb['ListenerDescriptions']) > 0:
                for listener in lb['ListenerDescriptions']:
                    protocol = listener['Listener']['Protocol']
                    if protocol == 'HTTPS' or protocol == 'SSL':
                        pass
                    else:
                        flag = False
                        result = False
                        failReason = 'Load balancer listeners are not using secure protocol (HTTPS or SSL)'
                        offenders.append(lb['LoadBalancerName'])
                    if not flag:
                        break

            else:
                result = False
                failReason = 'Load balancer listeners are not using secure protocol (HTTPS or SSL)'
                offenders.append(lb['LoadBalancerName'])

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
