import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks the compliance.py for s3 bucket versioning enabled
def s3_bucket_versioning_enabled(self, buckets):
    """

    :param buckets:
    :param self:
    :return dict: details of s3 bucket versioning enabled compliance.py
    """
    logger.info(" ---Inside s3 :: s3_bucket_versioning_enabled()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id1.20'
    compliance_type = "S3 bucket versioning enabled"
    description = "Checks if bucket versioning is enabled in s3 buckets."
    resource_type = "S3 Buckets"
    risk_level = 'Low'

    client = self.session.client('s3')
    # response = client.list_buckets()

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            resp = client.get_bucket_versioning(
                Bucket=bucket_name,
            )
            status = resp['Status']
        except KeyError:
            result = False
            failReason = "Either bucket versioning is not enabled or configuration not found"
            offenders.append(bucket_name)
            continue

        if not status == 'Enabled':
            result = False
            failReason = "Either bucket versioning is not enabled or configuration not found"
            offenders.append(bucket_name)

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
