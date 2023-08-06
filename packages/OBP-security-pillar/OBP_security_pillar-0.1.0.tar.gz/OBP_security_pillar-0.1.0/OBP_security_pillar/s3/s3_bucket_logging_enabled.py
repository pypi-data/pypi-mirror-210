import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# checks the compliance.py for s3 bucket versioning enabled
def s3_bucket_logging_enabled(self, buckets):
    """

    :param buckets:
    :param self:
    :return dict:
    """
    logger.info(" ---Inside s3 :: s3_bucket_logging_enabled()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id1.16'
    compliance_type = "S3 bucket logging enabled"
    description = "Checks whether logging is enabled for your S3 buckets"
    resource_type = "S3 Buckets"
    risk_level = 'Medium'

    client = self.session.client('s3')
    # response = client.list_buckets()

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            resp = client.get_bucket_logging(
                Bucket=bucket_name,
            )
            if resp['LoggingEnabled'] is None:
                raise KeyError
        except KeyError:
            result = False
            failReason = "Bucket logging is not enabled"
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
