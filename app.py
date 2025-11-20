from flask import Flask
import boto3
import os

app = Flask(__name__)

# Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_KEY'), # access key for AWS account
    aws_secret_access_key=os.getenv('S3_ACCESS') # secret key for AWS account
)

@app.route("/")
def home():
    return "<p> URLGetter is live! </p>"