from flask import request
import boto3
import os
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

def upload_to_s3():
    s3_client_upload = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_KEY'), # access key for AWS account
    aws_secret_access_key=os.getenv('S3_ACCESS'), # secret key for AWS account
    region_name=os.getenv('REGION')
)   
    file = request.files['file']
    filecontent = file.read()
    # ensures provided file name is correct and won't break any methods down the line
    filename = secure_filename(file.filename)
    print(filename)    
    # Reference - https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/put_object.html
    try:
        response = s3_client_upload.put_object(
            Body = filecontent,
            Bucket = os.getenv('BUCKET_NAME'),
            Key = filename
        )
        print(response)
        return "Successful upload!"
        # return render_template('upload.html', flash="Successfully uploaded!")
    except ClientError as e:
        print(e)
        return "Unsuccessful upload"
        # return render_template('upload.html', flash="Error uploading file.")