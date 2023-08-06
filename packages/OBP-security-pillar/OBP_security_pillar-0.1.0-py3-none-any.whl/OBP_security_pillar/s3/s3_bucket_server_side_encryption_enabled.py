import logging
import botocore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def s3_bucket_server_side_encryption_enabled(self, buckets):
    logger.info(" ---Inside s3 :: s3_bucket_server_side_encryption_enabled()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id1.19'
    compliance_type = "S3 bucket server side encryption enabled"
    description = "Checks whether server side encryption is enabled for your S3 buckets"
    resource_type = "S3 Buckets"
    risk_level = 'High'

    client = self.session.client('s3')
    # response = client.list_buckets()

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            resp = client.get_bucket_encryption(
                Bucket=bucket_name
            )
            # print(resp)

        except botocore.exceptions.ClientError:
            result = False
            failReason = "Default server side encryption is not enabled for S3 Bucket"
            offenders.append(bucket_name)
            continue

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
