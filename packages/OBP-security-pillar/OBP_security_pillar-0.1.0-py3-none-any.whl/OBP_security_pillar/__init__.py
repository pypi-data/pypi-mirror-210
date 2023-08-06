from boto3 import session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


__author__ = 'Dheeraj Banodha'
__version__ = '0.1.0'


class aws_client:
    def __init__(self, **kwargs):
        """
        @param str aws_access_key_id: AWS Access Key ID
        @param str aws_secret_access_key: AWS Secret Access Key
        """

        if 'aws_access_key_id' in kwargs.keys() and 'aws_secret_access_key' in kwargs.keys():
            self.session = session.Session(
                aws_access_key_id=kwargs['aws_access_key_id'],
                aws_secret_access_key=kwargs['aws_secret_access_key'],
            )
        elif 'profile_name' in kwargs.keys():
            self.session = session.Session(profile_name=kwargs['profile_name'])

    from .rds import rds_compliance, list_rds_instances, list_rds_snapshots
    from .s3 import s3_compliance, list_s3_buckets
    from .ec2 import ec2_compliance, list_ec2_instances
    from .auto_scaling import auto_scaling_compliance
    from .cloudtrail import cloudtrail_compliance
    from .dynamodb import dynamodb_compliance
    from .guard_duty_enabled import guard_duty_enabled
    from .lambda_inside_vpc import lambda_inside_vpc
    # from .security_hub_enabled import security_hub_enabled
    from .elb_tls_https_listeners_only import elb_tls_https_listeners_only
    from .elb_logging_enabled import elb_logging_enabled

    # consolidate compliance.py details
    def get_compliance(self) -> list:
        """
        :return list: consolidated list  of compliance.py checks
        """
        logger.info(" ---Inside get_compliance()")

        regions = self.get_regions()

        compliance = [
            # self.security_hub_enabled(),

            self.elb_logging_enabled(),
            self.elb_tls_https_listeners_only(),

            # self.guard_duty_enabled(),
            # self.lambda_inside_vpc(),
        ]

        compliance.extend(self.rds_compliance(regions))
        compliance.extend(self.s3_compliance())
        compliance.extend(self.ec2_compliance(regions))
        compliance.extend(self.dynamodb_compliance())
        compliance.extend(self.auto_scaling_compliance())
        compliance.extend(self.cloudtrail_compliance())

        return compliance

    def get_regions(self):
        logger.info(" ---Inside utils :: get_regions()--- ")
        """Summary

        Returns:
            TYPE: Description
        """

        client = self.session.client('ec2', region_name='us-east-1')
        region_response = {}
        # try:
        region_response = client.describe_regions()
        # except botocore.exceptions.ClientError as error:
        #     if error.response['Error']['Code'] == 'AuthFailure':
        #         logger.error(f" AccessKey credentails not found here: {error}")
        #         return {
        #             'Result': 'Auth Failure',
        #             'failReason': 'Auth Failure',
        #             'Offenders': [],
        #             'ScoredControl': False,
        #             'Description': 'Auth Failure',
        #             'ControlId': 'Auth Failure'
        #         }
        # except botocore.exceptions.NoCredentialsError as e:
        #     logger.error(f" Unable to locate credentials: {e} ")
        #     return {
        #         'Result': 'Auth Failure',
        #         'failReason': 'Auth Failure',
        #         'Offenders': [],
        #         'ScoredControl': False,
        #         'Description': 'Auth Failure',
        #         'ControlId': 'Auth Failure'
        #     }

        logger.debug(region_response)
        regions = [region['RegionName'] for region in region_response['Regions']]
        return regions
