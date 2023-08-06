import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks the compliance for the ec2 volume in use check
def ec2_encrypted_volume(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ec2_encrypted_volume()")

    result = True
    failReason = ''
    offenders = []
    control_id = ''

    compliance_type = "Attached Ec2 volume are encrypted"
    description = "Checks if the EBS volumes that are in an attached state are encrypted."
    resource_type = "EC2"
    risk_level = 'High'

    regions = self.session.get_available_regions('ec2')

    for region in regions:
        try:
            client = self.session.client('ec2', region_name=region)
            marker = ''
            while True:
                if marker == '':
                    response = client.describe_volumes()
                else:
                    response = client.describe_volumes(
                        NextToken=marker
                    )
                for volume in response['Volumes']:
                    if  volume['State'] == 'in-use' and volume['Encrypted'] == 'False':
                        result = False
                        failReason = "Amazon EBS volume attached to EC2 instance is not encrypted"
                        offenders.append(volume['VolumeId'])
                        
                try:
                    marker = response['NextToken']
                    if marker == '':
                        break
                except KeyError:
                    break

        except ClientError as e:
            logger.warning("Something went wrong with the region {}: {}".format(region, e))

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