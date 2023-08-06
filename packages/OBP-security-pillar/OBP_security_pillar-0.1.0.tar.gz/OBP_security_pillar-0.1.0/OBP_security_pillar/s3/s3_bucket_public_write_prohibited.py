import logging
import botocore
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def s3_bucket_public_write_prohibited(self, buckets):
    logger.info(" ---Inside s3 :: s3_bucket_public_write_prohibited()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id1.18'
    compliance_type = "S3 bucket public write prohibited"
    description = "Checks whether public write is prohibited for your S3 buckets"
    resource_type = "S3 Buckets"
    risk_level = 'High'

    client = self.session.client('s3')
    # response = client.list_buckets()

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            resp = client.get_public_access_block(
                Bucket=bucket_name
            )
            # print(resp)

            public_access_block = resp['PublicAccessBlockConfiguration']
            if public_access_block['BlockPublicAcls'] == 'False':
                raise KeyError
            if public_access_block['IgnorePublicAcls'] == 'False':
                raise KeyError
            if public_access_block['BlockPublicPolicy'] == 'False':
                raise KeyError
            if public_access_block['RestrictPublicBuckets'] == 'False':
                raise KeyError

        except ClientError as e:
            result = False
            failReason = "The Block Public Access setting does not restrict public bucket ACLs or the public policies"
            offenders.append(bucket_name)
            continue
        except KeyError:
            result = False
            failReason = "The Block Public Access setting does not restrict public bucket ACLs or the public policies"
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
