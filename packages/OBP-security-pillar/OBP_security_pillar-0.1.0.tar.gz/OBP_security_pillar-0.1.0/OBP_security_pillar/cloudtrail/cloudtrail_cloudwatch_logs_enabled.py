import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def cloudtrail_cloudwatch_logs_enabled(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside cloudtrail :: cloudtrail_cloudwatch_logs_enabled()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id1.1'

    compliance_type = "cloud-trail cloudwatch logs enabled"
    description = "Checks whether AWS CloudTrail trails are configured to send logs to Amazon CloudWatch logs"
    resource_type = "CloudTrail"
    risk_level = 'Medium'
    
    regions = self.session.get_available_regions('cloudtrail')

    for region in regions:
        try:
            client = self.session.client('cloudtrail', region_name=region)
            marker = ''
            while True:
                if marker == '':
                    response = client.list_trails()
                else:
                    response = client.list_trails(
                        NextToken=marker
                    )

                for trail in response['Trails']:
                    trail_desc = client.describe_trails(
                        trailNameList=[
                            trail['TrailARN']
                        ]
                    )
                    try:
                        arn = trail_desc['CloudWatchLogsLogGroupArn']
                        if arn == '':
                            raise KeyError
                    except KeyError:
                        result = False
                        failReason = 'Amazon CloudTrail trail is not configured to send events to CloudWatch Logs for ' \
                                     'monitoring purposes '
                        offenders.append(trail['Name'])

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
