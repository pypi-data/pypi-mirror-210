import logging
from OBP_security_pillar.compliance import Compliance

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def driver(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside cloudtrail :: driver()")

    compliance_result = {
        "cloud-trail cloudwatch logs enabled": Compliance(
            'cloud-trail cloudwatch logs enabled',
            'Checks whether AWS CloudTrail trails are configured to send logs to Amazon CloudWatch logs',
            'CloudTrail'
        )
    }

    # result = True
    # failReason = ''
    # offenders = []
    # compliance_type = "cloud-trail cloudwatch logs enabled"
    # description = "Checks whether AWS CloudTrail trails are configured to send logs to Amazon CloudWatch logs"
    # resource_type = "CloudTrail"

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
                        compliance_result['cloud-trail cloudwatch logs enabled'].failReason = 'Amazon CloudTrail ' \
                                                                                              'trail is not ' \
                                                                                              'configured to send ' \
                                                                                              'events to CloudWatch ' \
                                                                                              'Logs for monitoring ' \
                                                                                              'purposes '
                        compliance_result['cloud-trail cloudwatch logs enabled'].result = False
                        compliance_result['cloud-trail cloudwatch logs enabled'].offender = trail['Name']

                try:
                    marker = response['NextToken']
                    if marker == '':
                        break                           
                except KeyError:
                    break

        except ClientError as e:
            logger.warning("Something went wrong with the region {}: {}".format(region, e))

    return compliance_result
