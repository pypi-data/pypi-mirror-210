import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# Checks the compliance for the ec2 imdsv2 check
def ec2_imdsv2_check(self, ec2_instances) -> dict:
    """
    :param ec2_instances:
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ec2_imdsv2_check()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id5.7'

    compliance_type = "EC2 IMDS v2 Enabled"
    description = "Checks whether your Amazon Elastic Compute Cloud (Amazon EC2) instance metadata version is " \
                  "configured with Instance Metadata Service Version 2 (IMDSv2) "
    resource_type = "EBS"
    risk_level = 'Medium'

    # regions = self.session.get_available_regions('ec2')

    for region, instances in ec2_instances.items():
        for instance in instances:
            if instance['MetadataOptions']['HttpTokens'] == 'optional':
                result = False
                failReason = 'the Instance Metadata Service Version 1 (IMDSv1) is in use for the verified ' \
                             'instance '
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
