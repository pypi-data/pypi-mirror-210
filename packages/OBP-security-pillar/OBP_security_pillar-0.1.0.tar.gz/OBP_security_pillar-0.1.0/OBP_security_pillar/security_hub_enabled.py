# import botocore
# import logging
#
# from botocore.exceptions import ClientError
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger()
#
#
# def security_hub_enabled(self) -> list:
#     logger.info(" ---Inside security_hub_enabled()")
#
#     result = True
#     failReason = ''
#     offenders = []
#     compliance_type = "security hub enabled"
#     description = "Checks if security hub is enabled or not"
#     resource_type = "Security hub"
#     risk_level = 'Medium'
#
#     regions = self.session.get_available_regions('securityhub')
#
#     for region in regions:
#         print(region)
#         client = self.session.client('securityhub', region_name=region)
#         try:
#             print('in try')
#             response = client.describe_hub()
#             print('in try 1')
#             # Scenario 1: SecurityHub is enabled for an AWS Account
#             if response:
#                 pass
#         except botocore.exceptions.ClientError as error:
#             print('in except')
#             # Scenario 2: SecurityHub is not enabled for an AWS account.
#             if error.response['Error']['Code'] == 'InvalidAccessException':
#                 result = False
#                 offenders = []
#                 failReason = "Security hub is not enabled in all the regions"
#             logger.warning("Something went wrong with the region {}: {}".format(region, e))
#
#     return [{
#         'Result': result,
#         'failReason': failReason,
#         'resource_type': resource_type,
#         'Offenders': offenders,
#         'Compliance_type': compliance_type,
#         'Description': description,
#         'Risk Level': risk_level
#     }]
