from flask import Flask, render_template, request, flash, redirect, url_for
import boto3
import os
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import logging

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

@app.route("/upload", methods = ['GET', 'POST'])
def upload():
    # Reference - https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        # filenames = []
        # for file in files:
        #     file.filename = secure_filename(file.filename)
        #     filenames.append(file.filename)
        
        # Reference - https://docs.aws.amazon.com/boto3/latest/guide/s3-uploading-files.html
        # Reference - https://docs.aws.amazon.com/boto3/latest/reference/customizations/s3.html#boto3.s3.transfer.S3Transfer.ALLOWED_UPLOAD_ARGS
        try:
            with open(file, "rb") as f:
                s3_client.upload_fileobj(
                    f, os.getenv('BUCKET_NAME'), str(filename))
                    # ExtraArgs={
                    #     'ACL': 'public-read'})
                # flash('Successful upload!')
            return redirect(url_for('upload'))
        except ClientError as e:
            logging.error(e)
            # flash('Unsuccessful upload - try again.')
            return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route("/geturl", methods=['POST'])
def geturl():
    if request.method == 'POST':
        # Reference - https://tedboy.github.io/flask/generated/generated/flask.Request.html
        
        data = request.get_json(silent=True) # silent set to True to avoid direct fails and return None
        app.logger.info(data)
        key = data['objectName']
        password = data['password']

        # key = request.form['objectName']
        # password = request.form['password']

        # checking if user passed appropriate .zip suffix for object name in S3 bucket
        if not key.endswith(".zip"):
            key += ".zip"
        
        # Reference - https://flask-bcrypt.readthedocs.io/en/1.0.1/
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        password_env = os.getenv('PASSWORD')
        checker = bcrypt.check_password_hash(password_hash, password_env)
        if checker:
            # Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html#S3.Client.get_object
            # check if object with the given key exists first
            try:
                response = s3_client.get_object(
                    Bucket=os.getenv('BUCKET_NAME'),
                    Key=key
                )
            except:
                msg = "Object with given name does not exist."
                return msg, 404
            # Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
            try:
                # Changed response to include key from JSON request
                response = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': os.getenv('BUCKET_NAME'), 'Key': key},
                    ExpiresIn=300,
                )
                # Reference - https://flask.palletsprojects.com/en/stable/errorhandling/
                return response, 200
            except:
                return "URL failed to be generated", 400
        else:
            msg = "Wrong password given."
            return msg, 401