import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks compliance for rds snapshot encrypted
def rds_snapshot_encrypted(self, rds_snapshots) -> dict:
    """
    :param rds_snapshots:
    :param self:
    :return:
    """
    logger.info(" ---Inside rds :: rds_snapshot_encrypted()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.79'

    compliance_type = "RDS snapshot encrypted"
    description = "Checks whether Amazon Relational Database Service (Amazon RDS) DB snapshots are encrypted"
    resource_type = "RDS"
    risk_level = 'Medium'

    # regions = self.session.get_available_regions('rds')

    for region, snapshots in rds_snapshots.items():
        for snapshot in snapshots:
            encryption = snapshot['Encrypted']
            if not encryption:
                result = False
                failReason = 'DB snapshot is not encrypted'
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
