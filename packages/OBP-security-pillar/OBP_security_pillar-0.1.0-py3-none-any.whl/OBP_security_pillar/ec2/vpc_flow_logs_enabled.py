import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# Ensure VPC flow logging is enabled in all VPCs (Scored)
def vpc_logging_enabled(self, regions) -> dict:
    logger.info(" ---Inside vpc_logging_enabled()--- ")
    """Summary

    Returns:
        TYPE: Description
    """
    result = True
    failReason = ""
    offenders = []
    control_id = 'Id3.102'
    compliance_type = "VPC flow logs enabled"
    description = "Ensure VPC flow logging is enabled in all VPCs"
    resource_type = "EC2"
    risk_level = 'High'

    # regions = self.session.get_available_regions('ec2')

    for n in regions:
        try:
            client = self.session.client('ec2', region_name=n)
            flowlogs = client.describe_flow_logs(
                #  No paginator support in boto atm.
            )
            activeLogs = []
            for m in flowlogs['FlowLogs']:
                if "vpc-" in str(m['ResourceId']):
                    activeLogs.append(m['ResourceId'])
            vpcs = client.describe_vpcs(
                Filters=[
                    {
                        'Name': 'state',
                        'Values': [
                            'available',
                        ]
                    },
                ]
            )
            for m in vpcs['Vpcs']:
                if not str(m['VpcId']) in str(activeLogs):
                    result = False
                    failReason = "VPC without active VPC Flow Logs found"
                    offenders.append(str(n) + " : " + str(m['VpcId']))
        except ClientError as e:
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                logger.info('---------Ec2 read access denied----------')
                result = False
                failReason = "Access Denied"
                break
            logger.warning("Something went wrong with the region {}: {}".format(n, e))

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
