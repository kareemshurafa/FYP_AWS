from flask import Flask, render_template, request, flash, redirect, url_for, session
import boto3
import os
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import logging
from dotenv import load_dotenv
# import zipfile
# from PIL import Image

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')
bcrypt = Bcrypt(app)

local = False

# For local testing:
if local:
    load_dotenv()

# Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_KEY'), # access key for AWS account
    aws_secret_access_key=os.getenv('S3_ACCESS'), # secret key for AWS account
    region_name=os.getenv('REGION')
)

# Reference - adadpted from https://flask.palletsprojects.com/en/stable/quickstart/
@app.route("/")
def home():
    if 'username' in session:
        return render_template('home.html', user=session['username'])
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Reference - https://flask-bcrypt.readthedocs.io/en/1.0.1/
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        password_env = os.getenv('VR_PASSWORD')
        checker = bcrypt.check_password_hash(password_hash, password_env)
        checker2 = username == os.getenv('VR_USERNAME')
        if checker and checker2:
            session['username'] = request.form.get('username')
            return redirect(url_for('home'))
        else:
            return render_template('login.html', flash="Username and/or password are incorrect.")
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/getlist")
def getlist():
    if 'username' in session:
        # Reference - https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/list_objects.html
        try:
            response = s3_client.list_objects(
                Bucket=os.getenv('BUCKET_NAME')
            )
            object_list = []
            contents = response["Contents"]
            for content in contents:
                object_list.append(str(content['Key']))
            return render_template('getlist.html', list=object_list)
        except ClientError as e:
            logging.error(e)
            return render_template('getlist.html', flash="Unknown error occured during operation.")
    else:
        return redirect(url_for('login'))


@app.route("/delete", methods = ['GET', 'POST'])
def delete():
    if 'username' in session:
        if request.method =='POST':
            file = request.form.get('file')

            # Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html#S3.Client.get_object
            # check if object with the given key exists first
            try:
                response = s3_client.get_object(
                    Bucket=os.getenv('BUCKET_NAME'),
                    Key=file
                )
            except ClientError as e:
                logging.error(e)
                return render_template('delete.html', flash="File name does not exist.")
            # Reference - https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/delete_object.html
            try:
                response = s3_client.delete_object(
                    Bucket = os.getenv('BUCKET_NAME'),
                    Key=file
                )
                print(response)
                return render_template('delete.html', flash="Successfully deleted!")
            except ClientError as e:
                logging.error(e)
                return render_template('delete.html', flash="Unexpected error occured whilst deleting file")
        return render_template('delete.html', flash='')
    else:
        return redirect(url_for('login'))

@app.route("/rename", methods = ['GET', 'POST'])
def rename():
    if 'username' in session:
        if request.method =='POST':
            old_file = request.form.get('old_name')
            new_file = request.form.get('new_name')

            # Reference - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html#S3.Client.get_object
            # check if object with the given key exists first
            try:
                response = s3_client.get_object(
                    Bucket=os.getenv('BUCKET_NAME'),
                    Key=old_file
                )
            except ClientError as e:
                logging.error(e)
                return render_template('rename.html', flash="File name does not exist.")
            # Reference - https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/copy_object.html
            # copying over the original object with a new name - then we delete the old object
            # NEED TO CHECK FILE NAME if it's original + valid
            try:
                response = s3_client.copy_object(
                    Bucket=os.getenv('BUCKET_NAME'),
                    CopySource = {
                        'Bucket': os.getenv('BUCKET_NAME'),
                        'Key': old_file
                    },
                    Key=new_file
                )
            except ClientError as e:
                logging.error(e)
                return render_template('rename.html', flash="Error during copying operation.")
            # Reference - https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/delete_object.html
            # delete old object
            try:
                response = s3_client.delete_object(
                    Bucket = os.getenv('BUCKET_NAME'),
                    Key=old_file
                )
                print(response)
                return render_template('rename.html', flash="Successfully renamed file!")
            except ClientError as e:
                logging.error(e)
                return render_template('rename.html', flash="Unexpected error occured whilst deleting old file")
        return render_template('rename.html', flash='')
    else:
        return redirect(url_for('login'))


@app.route("/upload", methods = ['GET', 'POST'])
def upload():
    if 'username' in session:
        # Reference - https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
        if request.method == 'POST':
            file = request.files['file']
            filecontent = file.read()
            filename = secure_filename(file.filename)
            print(filename)
            # Reference - https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/put_object.html
            try:
                response = s3_client.put_object(
                    Body = filecontent,
                    Bucket = os.getenv('BUCKET_NAME'),
                    Key = filename
                )
                print(response)
                return render_template('upload.html', flash="Successfully uploaded!")
            except ClientError as e:
                logging.error(e)
                return render_template('upload.html', flash="Error uploading file.")
                
            # # Reference - https://docs.djangoproject.com/fr/2.2/topics/http/file-uploads/
            # files = request.files.getlist('file')
            # print("file: ")
            # print(files)

        return render_template('upload.html', flash="")
    else:
        return redirect(url_for('login'))

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
        password_env = os.getenv('VR_PASSWORD')
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