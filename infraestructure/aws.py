import boto3
import os

def init_aws_client(type: str):

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    print(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    client = boto3.client(
        type,
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    )
    return client