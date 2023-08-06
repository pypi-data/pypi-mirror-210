import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks the compliance for the ec2_instance_multiple_eni_check
def ec2_instance_multiple_eni_check(self, ec2_instances) -> dict:
    """
    :param ec2_instances:
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ec2_instance_multiple_eni_check()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id18.1'

    compliance_type = "Ec2 Instance multiple eni check"
    description = "Checks if Amazon Elastic Compute Cloud (Amazon EC2) uses multiple ENIs (Elastic Network Interfaces)"
    resource_type = "EC2"
    risk_level = 'Medium'

    # regions = self.session.get_available_regions('ec2')

    for region, instances in ec2_instances.items():
        for instance in instances:
            if len(instance['NetworkInterfaces']) > 1:
                result = False
                failReason = 'Amazon Instance use multiple network interfaces'
                offenders.append(instance['InstanceId'])

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
