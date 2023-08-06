import logging

from OBP_security_pillar.ec2.ebs_snapshot_public_restorable_check import ebs_snapshot_public_restorable_check
from OBP_security_pillar.ec2.ec2_ebs_encryption_by_default import ec2_ebs_encryption_by_default
from OBP_security_pillar.ec2.ec2_imdsv2_check import ec2_imdsv2_check
from OBP_security_pillar.ec2.ec2_instance_managed_by_ssm import ec2_instance_managed_by_ssm
from OBP_security_pillar.ec2.ec2_instance_multiple_eni_check import ec2_instance_multiple_eni_check
from OBP_security_pillar.ec2.ec2_instance_profile_attached import ec2_instance_profile_attached
from OBP_security_pillar.ec2.ec2_volume_inuse_check import ec2_volume_inuse_check
from OBP_security_pillar.ec2.instance_in_vpc import instance_in_vpc
from OBP_security_pillar.ec2.ec2_encrypted_volume import ec2_encrypted_volume
from OBP_security_pillar.ec2.Incoming_ssh_disabled import incoming_ssh_disabled
from OBP_security_pillar.ec2.vpc_flow_logs_enabled import vpc_logging_enabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# list rds instances
def list_ec2_instances(self, regions) -> dict:
    """
    :param regions:
    :return:
    """
    logger.info(" ---Inside utils :: list_ec2_instances()--- ")
    ec2_instance_lst = {}

    for region in regions:
        client = self.session.client('ec2', region_name=region)
        marker = ''
        while True:
            if marker == '':
                response = client.describe_instances()
            else:
                response = client.describe_instances(
                    NextToken=marker
                )
            for reservation in response['Reservations']:
                ec2_instance_lst.setdefault(region, []).extend(reservation['Instances'])

            try:
                marker = response['NextToken']
                if marker == '':
                    break
            except KeyError:
                break
    return ec2_instance_lst


def ec2_compliance(self, regions) -> list:
    """
    :param regions:
    :param self:
    :return:
    """
    logger.info(" ---Inside ec2 :: ec2_compliance()")

    ec2_instances = self.list_ec2_instances(regions)
    # print(ec2_instances)

    response = [
        ec2_ebs_encryption_by_default(self, regions),
        ec2_imdsv2_check(self, ec2_instances),
        ec2_instance_managed_by_ssm(self, ec2_instances),
        ec2_instance_multiple_eni_check(self, ec2_instances),
        ec2_instance_profile_attached(self, ec2_instances),
        ec2_volume_inuse_check(self, regions),
        ebs_snapshot_public_restorable_check(self, regions),
        # instance_in_vpc(self),
        # ec2_encrypted_volume(self),
        incoming_ssh_disabled(self, regions),
        vpc_logging_enabled(self, regions)
    ]

    return response
