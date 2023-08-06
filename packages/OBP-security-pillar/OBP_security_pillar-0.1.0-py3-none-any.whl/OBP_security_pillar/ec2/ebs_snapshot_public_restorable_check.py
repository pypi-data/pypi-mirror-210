import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks the compliance for ebs snapshot public restorable check
def ebs_snapshot_public_restorable_check(self, regions) -> dict:
    """
    :param regions:
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ebs_snapshot_public_restorable_check()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.29'

    compliance_type = "EBS snapshot public restorable check"
    description = "Checks whether Amazon Elastic Block Store (Amazon EBS) snapshots are not publicly restorable"
    resource_type = "EC2"
    risk_level = 'High'

    # regions = self.session.get_available_regions('ec2')

    client_sts = self.session.client('sts')
    account_id = client_sts.get_caller_identity()['Account']

    for region in regions:
        try:
            client = self.session.client('ec2', region_name=region)

            marker = ''
            while True:
                if marker == '':
                    response = client.describe_snapshots(
                        Filters=[
                            {
                                'Name': 'status',
                                'Values': ['completed']
                            }
                        ],
                        OwnerIds=[account_id]
                    )
                else:
                    response = client.describe_snapshots(
                        Filters=[
                            {
                                'Name': 'status',
                                'Values': 'completed'
                            }
                        ],
                        OwnerIds=[account_id],
                        NextToken=marker
                    )

                for snapshot in response['Snapshots']:
                    response_attribute = client.describe_snapshot_attribute(
                        Attribute='createVolumePermission',
                        SnapshotId=snapshot['SnapshotId']
                    )

                    for permission in response_attribute['CreateVolumePermissions']:
                        try:
                            if permission['Group'] == 'all':
                                result = False
                                failReason = 'snapshot is public restorable'
                                offenders.append(snapshot['SnapshotId'])
                        except KeyError:
                            pass

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
