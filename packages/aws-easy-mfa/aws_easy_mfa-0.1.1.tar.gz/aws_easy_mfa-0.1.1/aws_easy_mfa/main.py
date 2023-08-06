from functools import wraps
import boto3
from .utilities import get_mfa_credentials
from .utilities import create_boto3_session


def aws_easy_mfa(mfa_device_arn=None,
                 mfa_token_code=None,
                 duration_seconds=900,
                 return_session=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Retrieve MFA session credentials if provided
            if mfa_device_arn and mfa_token_code:
                mfa_credentials = get_mfa_credentials(mfa_token_code,
                                                      mfa_device_arn,
                                                      duration_seconds)
            else:
                mfa_credentials = None

            # Create a Boto3 session using the MFA session credentials
            if mfa_credentials:
                session = create_boto3_session(mfa_credentials)
            else:
                session = boto3.Session()

            # Call the function with the Boto3 session as an argument
            result = func(*args, session=session, **kwargs)

            # Optionally return the session along with the result
            if return_session:
                return result, session
            else:
                return result

        return wrapper

    return decorator
