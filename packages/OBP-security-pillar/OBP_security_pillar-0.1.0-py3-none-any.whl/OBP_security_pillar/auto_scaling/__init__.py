import logging

from OBP_security_pillar.auto_scaling.launch_config_public_ip_disabled import launch_config_public_ip_disabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def auto_scaling_compliance(self) -> list:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside auto_scaling :: auto_scaling_compliance()")

    response = [
        # launch_config_public_ip_disabled(self),
    ]

    return response
