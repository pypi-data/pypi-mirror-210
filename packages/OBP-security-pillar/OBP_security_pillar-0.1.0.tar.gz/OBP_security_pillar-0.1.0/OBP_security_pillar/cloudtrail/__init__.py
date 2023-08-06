import logging

from OBP_security_pillar.cloudtrail.cloudtrail_cloudwatch_logs_enabled import cloudtrail_cloudwatch_logs_enabled
from OBP_security_pillar.cloudtrail.driver import driver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# returns the consolidated cloudtrail compliance
def cloudtrail_compliance(self) -> list:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside cloudtrail :: cloudtrail_compliance()")

    # response = []

    response = [
        cloudtrail_cloudwatch_logs_enabled(self),
    ]

    # result = driver(self)
    #
    # for item in result.values():
    #     response.append(item.compliance())

    return response

