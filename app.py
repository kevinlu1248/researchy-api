import os

from flask import Flask, request, render_template, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from modules.website import Website
from dotenv import load_dotenv

from db import engine, User

load_dotenv()
app = Flask("researchy-api")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    first = db.Column(db.String(255))
    last = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password(self.password_hash, password)

    def __repr__(self):
        return "<User(name='{} {}' email='{}')>".format(
            self.first, self.last, self.email
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    print(request.method)
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        # TODO: ADD FORM VALIDATION
        if (
            db.session.query(User.user_id)
            .filter_by(email=request.form["email"])
            .scalar()
            is None
        ):
            new_user = User(email=request.form["email"], password="")
            new_user.set_password(request.form["password"])
            db.session.add(new_user)
            db.session.commit()
            return redirect("/", 200)  # success
        else:
            return redirect("/signup", 200)  # failure


# THE API
@app.route("/api", methods=["POST"])
def api():
    body = request.form
    print(body)
    if not body:
        return make_response("Please provide a valid object.", 400)
    if "text" not in body and "url" not in body:
        return make_response("Please provide a text or url.", 400)
    display = Website(url=body.get("url", None), raw_html=body.get("text", None))
    return make_response(display.description, 200)


# running on https://researchy-api.herokuapp.com
# running on http://64.225.115.179/

if __name__ == "__main__":
    app.run(debug=False, port=5001)
