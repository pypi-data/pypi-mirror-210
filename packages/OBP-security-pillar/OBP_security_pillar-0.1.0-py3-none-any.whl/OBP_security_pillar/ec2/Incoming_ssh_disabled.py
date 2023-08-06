import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# Ensure no security groups allow ingress from 0.0.0.0/0 to port 22
def incoming_ssh_disabled(self, regions):
    logger.info(" ---Inside incoming_ssh_disabled()")
    """Summary

    Returns:
        TYPE: Description
    """
    result = True
    failReason = ""
    offenders = []
    control_id = 'Id1.7'
    compliance_type = "restricted-ssh"
    description = "Checks if the incoming SSH traffic for the security groups is accessible"
    resource_type = "EC2"
    risk_level = 'High'

    # regions = self.session.get_available_regions('ec2')

    for n in regions:
        try:
            client = self.session.client('ec2', region_name=n)
            response = client.describe_security_groups()
            for m in response['SecurityGroups']:
                if "0.0.0.0/0" in str(m['IpPermissions']):
                    for o in m['IpPermissions']:
                        try:
                            if int(o['FromPort']) <= 22 <= int(o['ToPort']) and '0.0.0.0/0' in str(o['IpRanges']):
                                result = False
                                failReason = "Found Security Group with port 22 open to the world (0.0.0.0/0)"
                                offenders.append(str(m['GroupId']))
                        except:
                            if str(o['IpProtocol']) == "-1" and '0.0.0.0/0' in str(o['IpRanges']):
                                result = False
                                failReason = "Found Security Group with port 22 open to the world (0.0.0.0/0)"
                                offenders.append(str(n) + " : " + str(m['GroupId']))
        except ClientError as e:
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
