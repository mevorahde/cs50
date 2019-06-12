import os, hashlib

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
        in_session = True
        user = session.get('user_name', None)
        return render_template('index.html', in_session=in_session, session_message="Logged in as {}".format(user))
    return render_template('index.html')



@app.route("/login", methods = ['POST'])
def login():
    if 'user_name' in session:
        in_session = True
        user = session.get('user_name', None)
        return render_template('books.html', in_session=in_session, session_message="Logged in as {}".format(user))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session['user_name'] = username
        d_password = hashlib.sha3_384(password.strip().encode('utf-8')).hexdigest()
        if db.execute("SELECT user_name, password FROM users WHERE user_name = :username AND password = :password",
                  {"username": username, "password": d_password}):
            books = db.execute("SELECT id, isbn, title, author, year FROM books").fetchall()
            user = session.get('user_name')
            in_session = True
            return render_template('books.html', books=books, in_session=in_session, session_message="Logged in as {}".format(user))
        else:
            return render_template("error.html", message="Invalid Username or Password.")


@app.route("/search", methods = ['POST'])
def search():
    book_results = True
    no_results = False
    user = session.get('user_name')
    search_request = request.form.get("search")
    in_session = True
    search_results = db.execute("SELECT id, isbn, title, author, year FROM books WHERE isbn ILIKE :search_request OR title ILIKE :search_request OR author ILIKE :search_request ", {"search_request": '%' + search_request + '%'}).fetchall()
    if db.execute("SELECT id, isbn, title, author, year FROM books WHERE isbn ILIKE :search_request OR title ILIKE :search_request OR author ILIKE :search_request ", {"search_request": '%' + search_request + '%'}).rowcount == 0:
        no_results = True
        return render_template('books.html', search_results=search_results, no_results=True, in_session=in_session,  message="No Results Returned!", session_message="Logged in as {}".format(user))
    return render_template('books.html', search_results=search_results, in_session=in_session, book_results=True, no_results=False, session_message="Logged in as {}".format(user))


@app.route("/logout")
def logout():
    user = session.pop('user_name', None)
    value_now = session.get('user_name', None)
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
    hash_pass = hashlib.sha3_384(password.encode()).hexdigest()
    db.execute("INSERT INTO users (user_name, password, email) VALUES (:username, :password, :email)",
        {"username": username, "password": hash_pass, "email": email})
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
