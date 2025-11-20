from flask import Flask
import boto3
import os

app = Flask(__name__)

# Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_KEY'), # access key for AWS account
    aws_secret_access_key=os.getenv('S3_ACCESS') # secret key for AWS account,
    region_name=os.getenv('REGION')
)

@app.route("/")
def home():
    return "<p> URLGetter is live! </p>"

@app.route("/geturl")
def geturl():
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': os.getenv('BUCKET_NAME'), 'Key': os.getenv('KEY_NAME')},
            ExpiresIn=3600,
        )
        return "<p> " + response + " <p>"
    except:
        return "<p> URL failed to be generated <p>"