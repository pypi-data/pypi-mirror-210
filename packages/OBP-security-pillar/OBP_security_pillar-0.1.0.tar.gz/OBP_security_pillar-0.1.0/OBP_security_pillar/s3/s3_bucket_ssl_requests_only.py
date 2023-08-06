import logging
import botocore
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def s3_bucket_ssl_requests_only(self, buckets):
    logger.info(" ---Inside s3 :: s3_bucket_ssl_requests_only()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.92'
    compliance_type = "S3 bucket SSL requests only"
    description = "Checks whether S3 buckets have policies that require requests to use Secure Socket Layer (SSL)."
    resource_type = "S3 Buckets"
    risk_level = 'High'

    client = self.session.client('s3')
    # response = client.list_buckets()

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            resp = client.get_bucket_policy(
                Bucket=bucket_name
            )
            ssl_requests_only = ""
            # print(resp)
            policy = json.loads(resp["Policy"])
            for i in policy["Statement"]:
                if i["Effect"] == "Deny" and i["Condition"] == {'Bool': {'aws:SecureTransport': 'false'}}:
                    ssl_requests_only = "True"
                    break
                elif i["Effect"] == "Allow" and i["Condition"] == {'Bool': {'aws:SecureTransport': 'true'}}:
                    ssl_requests_only = "True"
                    break

            if ssl_requests_only != "True":
                raise KeyError

        except botocore.exceptions.ClientError:
            result = False
            failReason = "An error occurred (NoSuchBucketPolicy) when calling the GetBucketPolicy operation: The bucket policy does not exist"
            offenders.append(bucket_name)
            continue

        except KeyError:
            result = False
            failReason = "The S3 buckets doesn't have policies that require requests to use Secure Socket Layer (SSL)"
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
