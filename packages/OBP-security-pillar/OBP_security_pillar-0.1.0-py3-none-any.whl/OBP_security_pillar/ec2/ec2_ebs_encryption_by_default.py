import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks the compliance for the ec2 ebs encryption by default
def ec2_ebs_encryption_by_default(self, regions) -> dict:
    """
    :param regions:
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ec2_ebs_encryption_by_default()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id1.4'
    compliance_type = "EC2 EBS Encryption by default"
    description = "Check that Amazon Elastic Block Store (EBS) encryption is enabled by default"
    resource_type = "EBS"
    risk_level = 'Medium'

    # regions = self.session.get_available_regions('ec2')

    for region in regions:
        try:
            client = self.session.client('ec2', region_name=region)
            response = client.get_ebs_encryption_by_default()

            if not response['EbsEncryptionByDefault']:
                result = False
                failReason = 'encryption is not enabled'

        except ClientError as e:
            logger.error("Something went wrong with the region {}: {}".format(region, e))

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
