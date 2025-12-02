from flask import Flask
import boto3
import os
from flask import request , jsonify
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_KEY'), # access key for AWS account
    aws_secret_access_key=os.getenv('S3_ACCESS'), # secret key for AWS account
    region_name=os.getenv('REGION')
)

@app.route("/")
def home():
    return "<p> URLGetter is live! </p>"

@app.route("/geturl", methods=['POST'])
def geturl():
    if request.method == 'POST':
        key = request.args.get('objectName')
        password = request.args.get('password')
        
        # Reference - https://flask-bcrypt.readthedocs.io/en/1.0.1/
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        password_env = os.getenv['PASSWORD']
        checker = bcrypt.check_password_hash(password_hash, password_env)
        if checker:
            # Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
            try:
                response = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': os.getenv('BUCKET_NAME'), 'Key': os.getenv('KEY_NAME')},
                    ExpiresIn=3600,
                )
                return "<p> URL successfully generated! <p>"
            except:
                return "<p> URL failed to be generated <p>"
        else:
            return "<p> Wrong password! <p>"