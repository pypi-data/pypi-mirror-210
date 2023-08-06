import logging

import botocore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def launch_config_public_ip_disabled(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside autoscaling :: launch_config_public_ip_disabled()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.12'
    compliance_type = "Launch configuration public ip disabled"
    description = "Checks if public ip is disabled in launch configuration or not"
    resource_type = "Auto Scaling"
    risk_level = 'High'

    regions = self.session.get_available_regions('autoscaling')

    for region in regions:
        try:
            client_asg = self.session.client('autoscaling', region_name=region)

            n_token = ''
            while True:
                if n_token == '' or n_token is None:
                    autoscaling_response = client_asg.describe_launch_configurations()
                else:
                    autoscaling_response = client_asg.describe_launch_configurations(
                        NextToken=n_token
                    )

                for lc in autoscaling_response['LaunchConfigurations']:
                    try:
                        if lc['AssociatePublicIpAddress']:
                            result = False
                            failReason = 'launch configuration public ip is enabled'
                            offenders.append(lc['LaunchConfigurationARN'])
                    except KeyError:
                        pass

                try:
                    n_token = autoscaling_response['NextToken']
                    if n_token == '':
                        break
                except KeyError:
                    break
        except botocore.exceptions.ClientError:
            pass

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
