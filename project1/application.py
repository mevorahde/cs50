import os

from flask import Flask, session, render_template, request
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
    return render_template('index.html')


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("user_name")
    password = request.form.get("password")
    if db.execute("SELECT user_name, password FROM users WHERE user_name = :username AND password = :password", {"username" :username, "password": password}):
        return render_template("success.html")
    else:
        return render_template("error.html", message="Invalid Username or Password.")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    if db.execute("SELECT * FROM users WHERE user_name = :username", {"username": str(username)}).rowcount == 1:
        return render_template("error.html", message="The username you entered already exists. Please enter in a different username.")
    if db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount == 1:
        return render_template("error.html", message="The email you entered already exists. Please enter in a different email.")
    db.execute("INSERT INTO users (user_name, password, email) VALUES (:username, :password, :email)",
        {"username": username, "password": password, "email": email})
    db.commit()
    return render_template("success.html")


if __name__ == "__main__":
    app.run()
