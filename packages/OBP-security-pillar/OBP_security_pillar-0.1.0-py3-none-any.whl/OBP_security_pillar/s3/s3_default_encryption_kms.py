import logging
import botocore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def s3_default_encryption_kms(self, buckets):
    logger.info(" ---Inside s3 :: s3_default_encryption_kms()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.93'
    compliance_type = "S3 bucket default encryption KMS"
    description = "Checks whether S3 buckets are encrypted with AWS Key Management Service(AWS KMS)."
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
            rules = resp['ServerSideEncryptionConfiguration']['Rules']
            # print(rules)
            for i in rules:
                if i['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != 'aws:kms':
                    raise KeyError

        except botocore.exceptions.ClientError:
            result = False
            failReason = "Default server side encryption is not enabled for S3 Bucket"
            offenders.append(bucket_name)
            continue

        except KeyError:
            result = False
            failReason = "The S3 buckets are not encrypted with AWS Key Management Service(AWS KMS)"
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
