import os, smtplib, ev

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from flask_login import login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        return render_template('index.html', user_name='user_name', message="Logged in as {} | ".format(session['user_name']))
    return render_template('index.html')


@app.route("/login", methods = ['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    session['user_name'] = username
    
    if db.execute("SELECT user_name, password FROM users WHERE user_name = :username AND password = :password AND Is_Temp_Password = 1",
                   {"username": username, "password": password}):
        return render_template("create-new-password.hmtl")
    elif db.execute("SELECT user_name, password FROM users WHERE user_name = :username AND password = :password",
                  {"username": username, "password": password}):
        return redirect(url_for("index"))
    else:
        return render_template("error.html", message="Invalid Username or Password.")
    
    
@app.route("/logout")
def logout():
    del session['user_name']
    return redirect(url_for("index"))


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


@app.route("/reset-password", methods=["POST"])
def reset_password():
    email = request.form.get("email")
    temp_password = ev.os.environ['temp_password']
    user_id = db.execute("SELECT user_id FROM users WHERE email = :email",
                  {"email": email})
    if db.execute("SELECT user_id FROM users WHERE email = :email",
                  {"email": email}).rowcount == 1:
        db.execute("UPDATE users SET password = :temp_password, is_temp_password = '1' WHERE user_id = (SELECT user_id FROM users WHERE email = :email)",
                   {"temp_password": temp_password, "email": email})
        db.commit()
        try:
            send_email = ev.os.environ['email']
            password = ev.os.environ['password']
        
            subject = ev.os.environ['subject']
            message = ev.os.environ['message']
        
            msg = MIMEMultipart()
            msg['From'] = send_email
            msg['To'] = email
            msg['Subject'] = subject
        
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP('smtp.live.com', 587)
            server.starttls()
            server.login(email, password)
            text = msg.as_string()
            server.sendmail(send_email, email, text)
            server.quit()
        except Exception as e:
            print(e.message, e.args)
        finally:
            return render_template("success.html",
                                   message="Your password has been changed. Please check your email for your temp password and login.")
    else:
        return render_template("error.html", message="Invalid Email.")


@app.route("/new-password", methods=["POST"])
@login_required
def new_password():
    user_id = db.execute("SELECT user_id FROM users WHERE user_name = :user_name",
                  {"user_name": session['user_name']})
    db.execute("UPDATE users SET password = :new_password, is_temp_password = '0' WHERE user_id = :user_id",
               {"new_password": new_password, "user_id": user_id})
    db.commit()
    return redirect(url_for("index"))

    
if __name__ == "__main__":
    app.run()
