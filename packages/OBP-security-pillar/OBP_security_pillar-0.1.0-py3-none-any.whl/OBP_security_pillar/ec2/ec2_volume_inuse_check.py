import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks the compliance for the ec2 volume in use check
def ec2_volume_inuse_check(self, regions) -> dict:
    """
    :param regions:
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ec2_volume_inuse_check()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.37'

    compliance_type = "Ec2 volume in use"
    description = "Checks if EBS volumes are attached to EC2 instances"
    resource_type = "EC2"
    risk_level = 'Medium'

    # regions = self.session.get_available_regions('ec2')

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
                    state = volume['State']
                    if state == 'available':
                        result = False
                        failReason = "Amazon EBS volume is not attached to any EC2 instance"
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
