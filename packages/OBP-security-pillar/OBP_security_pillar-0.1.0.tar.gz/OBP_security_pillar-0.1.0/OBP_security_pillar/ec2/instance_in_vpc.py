import botocore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def instance_in_vpc(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 : instance_in_vpc()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.67'

    compliance_type = "EC2 instance In VPC"
    description = "Checks if your EC2 instances belong to a virtual private cloud (VPC)"
    resource_type = "EC2 Instance"
    risk_level = 'Medium'

    regions = self.session.get_available_regions('ec2')

    for region in regions:
        try:
            client = self.session.client('ec2', region_name=region)
            marker = ''
            while True:
                response = client.describe_instances(
                    MaxResults=1000,
                    NextToken=marker
                )
                if len(response['Reservations']) > 0:
                    for reservation in response['Reservations']:
                        for instance in reservation['Instances']:
                            try:
                                vpc_id = instance['VpcId']
                                if vpc_id == '' or vpc_id is None:
                                    raise KeyError
                            except KeyError:
                                result = False
                                failReason = "Instances does not belong to any VPC"
                                offenders.append(instance['InstanceId'])

                try:
                    marker = response['NextToken']
                    if marker == '':
                        break
                except KeyError:
                    break
        except botocore.exceptions.ClientError as e:
            logger.error('Something went wrong with region {}: {}'.format(region, e))

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
