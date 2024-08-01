from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Directory where the downloaded image will be stored
IMAGE_DIR = os.path.join('static', 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

def download_image_from_s3():
    s3_client = boto3.client('s3')
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    OBJECT_NAME = os.environ.get("OBJECT_NAME")
    local_file_name = os.path.join(IMAGE_DIR, 'background.jpg')
    try:
        s3_client.download_file(BUCKET_NAME, OBJECT_NAME, local_file_name)
        logging.info(f"Downloaded image from S3: s3://{BUCKET_NAME}/{OBJECT_NAME}")
    except Exception as e:
        logging.error(f"Error downloading image from S3: {e}")

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "passwors"
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT"))
IMAGE_URL = os.getenv('IMAGE_URL', 'default_image.jpg') 

if IMAGE_URL:
    download_image_from_s3()
else:
        logging.error("S3 bucket name or object name environment variables are not set.")
# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE

)
output = {}
table = 'employee'

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}


# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(
    ["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])


@app.route("/", methods=['GET', 'POST'])
def home():
    
    header_names = os.getenv('HEADER_NAMES', 'Default Names')
    return render_template('addemp.html', header_names=header_names, background_image_url=IMAGE_URL )


@app.route("/app1", methods=['GET', 'POST'])
def home1():
    return render_template('addemp.html', background_image_url=IMAGE_URL)


@app.route("/app2", methods=['GET', 'POST'])
def home2():
    return render_template('addemp.html', background_image_url=IMAGE_URL)


@app.route("/app3", methods=['GET', 'POST'])
def home3():
    return render_template('addemp.html', background_image_url=IMAGE_URL)


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', background_image_url=IMAGE_URL)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(insert_sql, (emp_id, first_name,
                       last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, background_image_url=IMAGE_URL)


@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", background_image_url=IMAGE_URL)


@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()

        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]

    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], background_image_url=IMAGE_URL)


if __name__ == '__main__':

    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print("A color was set through environment variable -" + COLOR_FROM_ENV +
                  ". However, color from command line argument takes precendence.")
    elif COLOR_FROM_ENV:
        print(
            "No Command line argument. Color from environment variable =" + COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR +
              "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    app.run(host='0.0.0.0', port=81, debug=True)
