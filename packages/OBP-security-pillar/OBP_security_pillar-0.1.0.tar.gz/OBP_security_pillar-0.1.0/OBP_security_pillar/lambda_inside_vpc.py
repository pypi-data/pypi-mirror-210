import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# returns the list of lambda functions
def list_lambda_functions(client) -> dict:
    """
    :param client:
    :param self:
    :return:
    """
    logger.info(" ---Inside lambdafn.utils :: list_lambda_functions")

    function_lst = []

    marker = ''
    while True:
        if marker == '' or marker is None:
            response = client.list_functions()
        else:
            response = client.list_functions(
                Marker=marker
            )
        for fn in response['Functions']:
            function_lst.append(fn)

        try:
            marker = response['NextMarker']
            if marker == '':
                break
        except KeyError:
            break

    return function_lst


# checks the compliance for lambda-inside-vpc
def lambda_inside_vpc(self) -> dict:
    """
    :param self:
    :return:
    """
    logger.info(" ---Inside lambda :: lambda_inside_vpc()")

    result = True
    failReason = ''
    offenders = []
    control_id = 'Id3.72'

    compliance_type = "Lambda DLQ check"
    description = "Checks whether an AWS Lambda function is configured with a dead-letter queue."
    resource_type = "AWS Lambda"
    risk_level = 'Medium'

    regions = self.session.get_available_regions('lambda')

    for region in regions:
        try:
            client = self.session.client('lambda', region_name=region)
            function_lst = list_lambda_functions(client)

            for function in function_lst:
                try:
                    vpc_id = function['VpcConfig']['VpcId']
                except KeyError:
                    result = False
                    offenders.append(function['FunctionName'])
                    failReason = 'Lambda function is not VPC enabled'
        except ClientError as e:
            logger.error("Something went wrong with the region {}: {}".format(region, e))

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
