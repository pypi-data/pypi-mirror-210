import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def dynamodb_table_encrypted_kms(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside dynamodb :: dynamodb_table_encrypted_kms()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.27'
    compliance_type = "Dynamodb Table Encrypted KMS"
    description = "Checks if Amazon DynamoDB table is encrypted with AWS Key Management Service (KMS)"
    resource_type = "Dynamodb"
    risk_level = 'High'

    regions = self.session.get_available_regions('dynamodb')

    for region in regions:
        try:
            client = self.session.client('dynamodb', region_name=region)
            client_kms = self.session.client('kms', region_name=region)
            marker = ''
            while True:
                if marker == '':
                    response = client.list_tables()
                else:
                    response = client.list_tabled(
                        ExclusiveStartTableName=marker
                    )
                for table in response['TableNames']:
                    table_desc = client.describe_table(
                        TableName=table
                    )
                    try:
                        key_arn = table_desc['Table']['SSEDescription']['KMSMasterKeyArn']

                        kms_key = client_kms.describe_key(
                            KeyId=key_arn
                        )
                        key_manager = kms_key['KeyMetadata']['KeyManager']
                        if key_manager ==  'AWS':
                            result = False
                            failReason = "The Data on dynamodb table is not encrypted at rest using a " \
                                         "customer-provided KMS Customer Master Key (CMK) "
                            offenders.append(table)

                    except KeyError:
                        result = False
                        failReason = 'KMS encryption not enabled'
                        offenders.append(table)
                try:
                    marker = response['LastEvaluatedTableName']
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
