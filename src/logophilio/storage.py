import os
from dotenv import load_dotenv
import boto3
from django.conf import settings

__all__ = "s3"
load_dotenv()

s3 = boto3.resource(
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_S3_SECRET_ACCESS_KEY"),
    bucket="logophilio",
)
