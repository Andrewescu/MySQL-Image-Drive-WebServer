from flask import Flask, request, render_template, redirect, session
from mysql.connector import connect
import base64
import random
import string
import os


DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')



app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Create a connection to the MySQL database
cnx = connect(user=DATABASE_USERNAME, password=DATABASE_PASSWORD, host=DATABASE_HOST, database=DATABASE_NAME)
cursor = cnx.cursor(buffered=True)



@app.route("/", methods=["GET", "POST"])
def home_page():

    logged_in = session.get('logged_in', False)

    if logged_in == True:
        return render_template("homeLogged.html", username = session['username'])
    else:
        return render_template("home.html")

@app.route("/accountcreation", methods =["GET", "POST"])
def account_creation():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        query = f"SELECT * FROM users WHERE username = '{username}' "
        # Execute the query
        cursor.execute(query)
        # Fetch and check the result
        result = cursor.fetchone()
        if result != None:
            # The username already exists
            return redirect('/accountcreation?error=username')
        else:
            # The username does not exist already and can be created
            # Insert the row into the table
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            # Commit the changes
            cnx.commit()
            return redirect("/login")

    else:
        error = request.args.get('error', None)
        if error != None:
            return render_template("creationError.html")
        else:
            return render_template("creation.html")

@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Construct the SELECT statement
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        # Execute the query
        cursor.execute(query)

        # Fetch and check the result
        result = cursor.fetchone()
        if result:
            # The username and password match a row in the table
            session['logged_in'] = True
            session['username'] = username
            return redirect("/")
        else:
            # The username and password do not match any rows in the table
            return render_template("loginError.html")

        

    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
  # Clear session data
  session.clear()
  return redirect('/')


@app.route("/upload", methods=["GET", "POST"])
def upload_image():

    logged_in = session.get('logged_in', False)

    if logged_in == True:
        if request.method == "POST":
            # Get the image data from the request
            image_data = request.files["image"].read()  
            image_data = base64.b64encode(image_data)
            username = session["username"]
            uniqueID = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # Save the image to the MySQL database
            cursor.execute("INSERT INTO images (username, data, uniqueid) VALUES (%s, %s, %s)", (username, image_data, uniqueID))
            cnx.commit()
            return redirect("/")
        else:
            return render_template("upload_form.html")
    else:
        return redirect("/login")


@app.route("/view")
def view_images():

    logged_in = session.get('logged_in', False)

    if logged_in == True:
        # Retrieve all the images from the database
        query = "SELECT * FROM images"
        cursor.execute(query)
        images = cursor.fetchall()
        # Render the images template, passing the images data as a parameter
        return render_template("images.html", images=images)
    else:
        return redirect("/login")


if __name__ == "__main__":
    app.run()
