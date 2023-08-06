import logging

from OBP_security_pillar.dynamodb.dynamodb_table_encrypted_kms import dynamodb_table_encrypted_kms

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# returns the consolidated dynamodb compliance
def dynamodb_compliance(self) -> list:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside dynamodb :: dynamodb_compliance()")

    response = [
        dynamodb_table_encrypted_kms(self),
    ]

    return response
