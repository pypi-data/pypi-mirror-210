import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks compliance for rds snapshot public prohibited
def rds_snapshots_public_prohibited(self, rds_snapshots) -> dict:
    """
    :param rds_snapshots:
    :param self:
    :return:
    """
    logger.info(" ---Inside rds :: rds_snapshots_public_prohibited")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id1.11'

    compliance_type = "RDS snapshot public prohibited"
    description = "Checks if Amazon Relational Database Service (Amazon RDS) snapshots are public"
    resource_type = "RDS"
    risk_level = 'High'

    # regions = self.session.get_available_regions('rds')

    for region, snapshots in rds_snapshots.items():
        client = self.session.client('rds', region_name=region)
        for snapshot in snapshots:
            res = client.describe_db_snapshot_attributes(
                DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier']
            )
            for attribute in res['DBSnapshotAttributesResult']['DBSnapshotAttributes']:
                if attribute['AttributeName'] == 'restore':
                    if 'all' in attribute['AttributeValues']:
                        result = False
                        failReason = 'Amazon RDS database snapshot is publicly accessible and available for ' \
                                     'any AWS account to copy or restore it '
                        offenders.append(snapshot['DBSnapshotIdentifier'])

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
