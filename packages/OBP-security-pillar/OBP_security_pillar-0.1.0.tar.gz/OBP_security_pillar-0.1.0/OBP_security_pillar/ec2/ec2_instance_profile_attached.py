import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# Checks the compliance for ec2 instance profile attached
def ec2_instance_profile_attached(self, ec2_instances) -> dict:
    """
    :param ec2_instances:
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ec2_instance_profile_attached()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.33'

    compliance_type = "Ec2 instance profile attached"
    description = "Checks if an Amazon Elastic Compute Cloud (Amazon EC2) instance has an Identity and Access " \
                  "Management (IAM) profile attached to it "
    resource_type = "EC2"
    risk_level = 'Medium'

    # regions = self.session.get_available_regions('ec2')

    for region, instances in ec2_instances.items():
        for instance in instances:
            try:
                profile = instance['IamInstanceProfile']['Id']
            except KeyError:
                result = False
                failReason = "Iam instance profile does not exist"
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
