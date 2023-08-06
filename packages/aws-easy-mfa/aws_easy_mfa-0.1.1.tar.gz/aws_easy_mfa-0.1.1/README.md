# aws_easy_mfa

`aws_easy_mfa` is a simple wrapper for AWS's boto3 that makes it much simpler to use with MFA.  

Simply wrap any function invoking a boto3 session with the `aws_easy_mfa` decorator and you're off!  `aws_easy_mfa` will take care of all the tedius MFA login steps.


## Installation

You can install `aws_easy_mfa` via pip 

```python
pip install aws-easy-mfa
```

## A simple example

Using boto3 to list bucket names in s3 with the `aws_easy_mfa` decorator.

```python
from aws_easy_mfa import aws_easy_mfa

@aws_easy_mfa(mfa_device_arn='arn-of-the-mfa-device', 
              mfa_token_code='code-from-token')
def list_s3_buckets(session=None):
    # Create an S3 client using the session
    s3_client = session.client('s3')

    # List all S3 buckets
    response = s3_client.list_buckets()

    # Extract the bucket names from the response
    buckets = response['Buckets']
    bucket_names = [bucket['Name'] for bucket in buckets]
    return bucket_names

```

## Optional arguments

You can control your MFA timeout by including `duration_seconds` as shown below

```python
@aws_easy_mfa(mfa_device_arn='arn-of-the-mfa-device', 
              mfa_token_code='code-from-token',
              duration_seconds=3600)
def list_s3_buckets(session=None):
    ...
```

In addition, if you would like your MFA-authorized sesssion for further usage, you can add the `return_session=True` flag to your decorator, like this


```python
@aws_easy_mfa(mfa_device_arn='arn-of-the-mfa-device', 
              mfa_token_code='code-from-token',
              duration_seconds=3600,
              return_session=True)
def list_s3_buckets(session=None):
    ...
```

The session is returned as a second argument.  So for example instead of 

```python
bucket_names = list_s3_buckets()
```

enabling this flag returns your session as 

```python
bucket_names, session = list_s3_buckets()
```

## Direct session retrieval

You can also create an MFA session without usage of the decorator as shown below:

```python
from aws_easy_mfa.utilities import get_mfa_credentials, create_boto3_session

# get credentials 
credentials = get_mfa_credentials(mfa_device_arn='arn-of-the-mfa-device', 
                                  mfa_token_code='code-from-token',
                                  duration_seconds)

# generate mfa-authorized session
session = create_boto3_session(credentials)
```