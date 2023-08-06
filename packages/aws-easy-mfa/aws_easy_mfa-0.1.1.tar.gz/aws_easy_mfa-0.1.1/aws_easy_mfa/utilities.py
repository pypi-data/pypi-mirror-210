import boto3


def get_mfa_credentials(mfa_token_code, mfa_device_arn, duration_seconds=3600):
    # Create a Boto3 client for STS
    sts_client = boto3.client('sts')

    # Call the get_session_token API to retrieve a session token
    response = sts_client.get_session_token(
        DurationSeconds=duration_seconds,
        SerialNumber=mfa_device_arn,
        TokenCode=mfa_token_code
    )

    return response['Credentials']


def create_boto3_session(mfa_credentials):
    # Create a Boto3 session using the MFA session credentials
    session = boto3.Session(
        aws_access_key_id=mfa_credentials['AccessKeyId'],
        aws_secret_access_key=mfa_credentials['SecretAccessKey'],
        aws_session_token=mfa_credentials['SessionToken']
    )

    return session
