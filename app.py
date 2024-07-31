from flask import Flask, render_template
import socket
import mysql.connector
import os
import boto3
import logging

app = Flask(__name__)

DB_Host = os.environ.get('DB_Host') or "mysql"
DB_Database = os.environ.get('DB_Database') or "mysql"
DB_User = os.environ.get('DB_User')
DB_Password = os.environ.get('DB_Password') 
groupname = os.environ.get("GROUP_NAME")
image_uri = os.environ.get("Image_Uri")
AWS_REGION = os.environ.get("AWS_REGION")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

# Logging configuration
logging.basicConfig(level=logging.INFO)
logging.info(f"Background image URL: {image_uri}")

# Function to download image from S3
def download_image(bucket_name, image_key, download_path):
    s3 = boto3.client('s3', region_name=AWS_REGION)
    try:
        s3.download_file(bucket_name, image_key, download_path)
        logging.info(f"Downloaded image from S3: {image_key}")
    except Exception as e:
        logging.error(f"Failed to download image: {e}")

# Ensure the image_uri variable is set
if image_uri:
    download_image(S3_BUCKET_NAME, image_uri, 'static/success.jpg')

@app.route("/")
def main():
    db_connect_result = False
    err_message = ""
    try:
        mysql.connector.connect(host=DB_Host, database=DB_Database, user=DB_User, password=DB_Password)
        color = '#39b54b'
        db_connect_result = True
    except Exception as e:
        color = '#ff3f3f'
        err_message = str(e)

    return render_template('hello.html', 
                           debug="Environment Variables: DB_Host=" + (os.environ.get('DB_Host') or "Not Set") + 
                           "; DB_Database=" + (os.environ.get('DB_Database') or "Not Set") + 
                           "; DB_User=" + (os.environ.get('DB_User') or "Not Set") + 
                           "; DB_Password=" + (os.environ.get('DB_Password') or "Not Set") + 
                           "; " + err_message, 
                           db_connect_result=db_connect_result, 
                           name=socket.gethostname(), 
                           color=color, 
                           image_uri=image_uri, 
                           groupname=groupname)

@app.route("/debug")
def debug():
    color = '#2196f3'
    return render_template('hello.html', 
                           debug="Environment Variables: DB_Host=" + (os.environ.get('DB_Host') or "Not Set") + 
                           "; DB_Database=" + (os.environ.get('DB_Database') or "Not Set") + 
                           "; DB_User=" + (os.environ.get('DB_User') or "Not Set") + 
                           "; DB_Password=" + (os.environ.get('DB_Password') or "Not Set"), 
                           color=color)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
