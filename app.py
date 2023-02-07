import requests

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Apology function to issue an error message
def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, message=message), code

# login in fucntion to ensure session is valid and keeps person logged in until clicks log out
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Function to get ISBN numbers of search
def get_isbn(search):

    isbn = []
    params_isbn = {"q": search}
    url_isbn = r'http://openlibrary.org/search.json'
    response = requests.get(url_isbn, params=params_isbn)
    query_isbn = response.json()
    for i in query_isbn["docs"]:
        try:
            isbn.append(i["isbn"][0])
        except (KeyError, TypeError, ValueError):
            isbn.append("unknown")
    for i in range(len(isbn)):
        try:
            if isbn[i] == "unknown":
                isbn.remove(isbn[i])
        except (IndexError):
            break
    return isbn

# Gets data from Open Library using ISBN numbers
def get_book(list):
    title = []
    author = []
    img = []
    isbn = list
    for i in range(0, len(isbn)):
        if i < 10:
            isbn[i] = str(isbn[i])
            url_data = "https://openlibrary.org/api/books?bibkeys=ISBN:" + isbn[i] + "&jscmd=data" + "&format=json"
            book_response = requests.get(url_data)
            url_img = "https://openlibrary.org/api/books?bibkeys=ISBN:" + isbn[i] + "&jscmd=viewapi" + "&format=json"
            img_response = requests.get(url_img)
            book_img = img_response.json()
            book_info = book_response.json()
            try:
                title.append(book_info["ISBN:" + isbn[i]]["title"])
            except (KeyError, TypeError, ValueError):
                title.append("Unknown")
            try:
                author.append(book_info["ISBN:" + isbn[i]]["authors"][0]["name"])
            except (KeyError, TypeError, ValueError):
                author.append("Unknown")
            try:
                img.append(book_img["ISBN:" + isbn[i]]["thumbnail_url"])
            except (KeyError, TypeError, ValueError):
                img.append("Image Not Availiable")
    return isbn, title, author, img

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///books.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting the form correctly)
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        special = ['!', '#', '$', '%', '.', '_', '&']

        if not username or not firstname or not lastname or not email:
            return apology("Error please try again", 400)

        # Confirm username not in use
        if db.execute("SELECT username FROM users WHERE username == ?", username):
            return apology("Username already in use", 403)

        # Confirm username not in use
        if db.execute("SELECT email FROM users WHERE email == ?", email):
            return apology("Email already in use", 403)

        # Ensure both password fields match
        elif password != confirmation:
            return apology("Passwords do not match", 403)

        # Ensure password is at least 6 characters
        elif len(password) < 6:
            return apology("Password must be at least 6 characters", 403)

        # Ensure has a special character
        elif all(x not in special for x in password):
            return apology("Must contain a special character (!, #, $, %, ., _, &)", 403)

        # Adds information to database
        else:
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (firstname, lastname, email, username, hash) VALUES(:firstname, :lastname, :email, :username, :hash)", firstname=firstname, lastname=lastname, email=email, username=username, hash=hash)
            return redirect("/")

    # reached form by GET load page
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("Please input username and password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["personid"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    # Loads main home page once logged in a shows all owned books
    ownedbooks = db.execute("SELECT bookid, personid FROM ownedbooks WHERE personid = :personid", personid=session["user_id"])
    bookid = []
    for row in ownedbooks:
        bookid.append(str(row["bookid"]))
    isbn, title, author, img = get_book(bookid)
    return render_template("index.html", isbn=isbn, title=title, author=author, img=img, len=range(len(title)))


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    # Search Function
    if request.method == "GET":
        return render_template("search.html")
    else:
        # Retrieves information using get book function and shows results on new page
        query = request.form.get("book")
        isbnlist = get_isbn(query)
        isbn, title, author, img = get_book(isbnlist)
        return render_template("results.html", isbn=isbn, title=title, author=author, img=img, len=range(len(title)))


# Adds book to my owned books database
@app.route("/addbooks", methods=["GET", "POST"])
@login_required
def addbooks():
    if request.method == "GET":
        return redirect("/")
    else:
        # Checks if book is already owned
        isbn = request.form.get("value")
        if db.execute("SELECT bookid, personid FROM ownedbooks WHERE bookid = :isbn AND personid = :personid", isbn=isbn, personid=session["user_id"]):
            return apology("Book already owned")
        else:
            # Removes book from wishlist if already added to wishlist and adds to owned books database
            if db.execute("SELECT bookid, personid FROM wishlist WHERE bookid = :isbn AND personid = :personid", isbn=isbn, personid=session["user_id"]):
                db.execute("DELETE FROM wishlist WHERE bookid = :isbn AND personid = :clientid", isbn=isbn, clientid=session["user_id"])
            db.execute("INSERT INTO ownedbooks (bookid, personid) VALUES(:isbn, :clientid)", isbn=isbn, clientid=session["user_id"])
            return redirect("/")


# Removes book from owned books database
@app.route("/removecurrent", methods=["GET", "POST"])
@login_required
def removecurrent():
    if request.method == "GET":
        return redirect("/")
    else:
        isbn = request.form.get("value")
        db.execute("DELETE FROM ownedbooks WHERE bookid = :isbn AND personid = :clientid", isbn=isbn, clientid=session["user_id"])
        return redirect("/")

# Adds book to wishlist database
@app.route("/addwishlist", methods=["GET", "POST"])
@login_required
def addwishlist():
    if request.method == "GET":
        return redirect("/")
    else:
        # Checks book not already in owned or in wishlist and if not adds book to wishlist database
        isbn = request.form.get("value")
        if db.execute("SELECT bookid, personid FROM ownedbooks WHERE bookid = :isbn AND personid = :personid", isbn=isbn, personid=session["user_id"]):
            return apology("Book already owned")
        elif db.execute("SELECT bookid, personid FROM wishlist WHERE bookid = :isbn AND personid = :personid", isbn=isbn, personid=session["user_id"]):
            return apology("Book already in wishlist")
        else:
            db.execute("INSERT INTO wishlist (bookid, personid) VALUES(:isbn, :clientid)", isbn=isbn, clientid=session["user_id"])
            return redirect("/mywishlist")


# Shows my current wishlist using teh wishlist database
@app.route("/mywishlist", methods=["GET", "POST"])
@login_required
def mywishlist():
    wishlist = db.execute("SELECT bookid, personid FROM wishlist WHERE personid = :personid", personid=session["user_id"])
    bookid = []
    for row in wishlist:
        bookid.append(str(row["bookid"]))
    isbn, title, author, img = get_book(bookid)
    return render_template("mywishlist.html", isbn=isbn, title=title, author=author, img=img, len=range(len(title)))


# Removes book from wishlist database
@app.route("/removewishlist", methods=["GET", "POST"])
@login_required
def removewishlist():
    if request.method == "GET":
        return redirect("/mywishlist")
    else:
        isbn = request.form.get("value")
        db.execute("DELETE FROM wishlist WHERE bookid = :isbn AND personid = :clientid", isbn=isbn, clientid=session["user_id"])
        return redirect("/mywishlist")