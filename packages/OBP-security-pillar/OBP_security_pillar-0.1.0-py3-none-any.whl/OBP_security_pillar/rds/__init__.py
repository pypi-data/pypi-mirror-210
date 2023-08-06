from .rds_automatic_minor_version_upgrade_enabled import *
from .rds_instance_public_access_check import *
from .rds_snapshot_encrypted import rds_snapshot_encrypted
from .rds_snapshots_public_prohibited import rds_snapshots_public_prohibited
from .rds_storage_encrypted import rds_storage_encrypted


# list rds instances
def list_rds_instances(self, regions) -> dict:
    """
    :param regions:
    :return:
    """
    logger.info(" ---Inside utils :: list_rds_instances()--- ")
    rds_instance_lst = {}

    for region in regions:
        client = self.session.client('rds', region_name=region)
        marker = ''
        while True:
            if marker == '':
                response = client.describe_db_instances(
                    MaxRecords=100
                )
            else:
                response = client.describe_db_instances(
                    MaxRecords=100,
                    Marker=marker
                )
            rds_instance_lst.setdefault(region, []).extend(response['DBInstances'])

            try:
                marker = response['Marker']
                if marker == '':
                    break
            except KeyError:
                break
    return rds_instance_lst


# list rds snapshots
def list_rds_snapshots(self, regions) -> dict:
    """
    :param regions:
    :return:
    """
    logger.info(" ---Inside utils :: list_rds_snapshots()--- ")
    rds_snapshot_lst = {}

    for region in regions:
        client = self.session.client('rds', region_name=region)
        marker = ''
        while True:
            if marker == '':
                response = client.describe_db_snapshots()
            else:
                response = client.describe_db_snapshots(
                    Marker=marker
                )
            rds_snapshot_lst.setdefault(region, []).extend(response['DBSnapshots'])

            try:
                marker = response['Marker']
                if marker == '':
                    break
            except KeyError:
                break
    return rds_snapshot_lst


def rds_compliance(self, regions) -> list:
    """
    :param regions:
    :param self:
    :return:
    """
    logger.info(" ---Inside rds :: rds_compliance()")

    rds_instances = self.list_rds_instances(regions)
    # print(rds_instances)
    rds_snapshots = self.list_rds_snapshots(regions)
    # print(rds_snapshots)

    response = [
        # rds_automatic_minor_version_upgrade_enabled(self, rds_instances),
        rds_instance_public_access_check(self, rds_instances),
        rds_snapshot_encrypted(self, rds_snapshots),
        rds_snapshots_public_prohibited(self, rds_snapshots),
        rds_storage_encrypted(self, rds_instances),
    ]

    return response
