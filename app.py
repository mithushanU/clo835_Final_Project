from flask import Flask, render_template, request
from pymysql import connections
import os

app = Flask(__name__)

# Environment Variables
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))
GROUP_NAME = os.environ.get('GROUP_NAME', 'Group Name')
BACKGROUND_URL = os.environ.get('BACKGROUND_URL', "https://grp3project-bucket.s3.amazonaws.com/grp3.jpg")

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', GROUP_NAME=GROUP_NAME, background=BACKGROUND_URL)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', GROUP_NAME=GROUP_NAME, background=BACKGROUND_URL)

@app.route("/addemp", methods=['POST'])
def add_emp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee (emp_id, first_name, last_name, primary_skill, location) VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    except Exception as e:
        print(f"Error: {e}")
        db_conn.rollback()
        emp_name = "Error occurred"
    finally:
        cursor.close()

    return render_template('addempoutput.html', name=emp_name)

@app.route("/getemp", methods=['GET', 'POST'])
def get_emp():
    return render_template("getemp.html", GROUP_NAME=GROUP_NAME, background=BACKGROUND_URL)

@app.route("/fetchdata", methods=['POST'])
def fetch_data():
    emp_id = request.form['emp_id']

    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    output = {}
    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        if result:
            output = {
                "emp_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "primary_skill": result[3],
                "location": result[4]
            }
        else:
            output["error"] = "Employee not found"
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

    return render_template("getempoutput.html",
                           id=output.get("emp_id", "N/A"),
                           fname=output.get("first_name", "N/A"),
                           lname=output.get("last_name", "N/A"),
                           primary_skill=output.get("primary_skill", "N/A"),
                           location=output.get("location", "N/A"),
                           GROUP_NAME=GROUP_NAME, background=BACKGROUND_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
