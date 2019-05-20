import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__,  instance_relative_config=True)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@app.route("/home")
def index():
    if 'user_name' in session:
        #user = session.get('user_name')
        return render_template('index.html', message="Login as {}".format(session.get('user_name')))
    return render_template('index.html',message="test")


@app.route("/login", methods = ['POST'])
def login():
    username = request.form.get("user_name")
    password = request.form.get("password")
    session['user_name'] = username
    #session_username = session['user_name']
    #return (session['user_name'])

    if db.execute("SELECT user_name, password FROM users WHERE user_name = :username AND password = :password",
                  {"username": username, "password": password}):
        return redirect(url_for("index"))
    else:
        return render_template("error.html", message="Invalid Username or Password.")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("passwordConfirm")
    email = request.form.get("email")
    if password != password_confirm:
        return render_template("error.html", message="'Password' and 'Confirm Password' fields do not match. Please have the passwords match.")
    if db.execute("SELECT user_name, password, email FROM users WHERE user_name = :username", {"username": str(username)}).rowcount == 1:
        return render_template("error.html", message="The username you entered already exists. Please enter in a different username.")
    if db.execute("SELECT user_name, password, email FROM users WHERE email = :email", {"email": email}).rowcount == 1:
        return render_template("error.html", message="The email you entered already exists. Please enter in a different email.")
    db.execute("INSERT INTO users (user_name, password, email) VALUES (:username, :password, :email)",
        {"username": username, "password": password, "email": email})
    db.commit()
    return render_template("success.html", message="Registeration complete, thanks for joining!")


@app.route("/forgot-password")
def forgot_password_page():
    return render_template("forgot-password.html")


@app.route("/email-sent")
def send_password_email():
    return render_template("forgot-password.html")


if __name__ == "__main__":
    app.run()
