from flask import Flask, request, render_template, make_response
from modules.website import Website
from dotenv import load_dotenv

from db import *

load_dotenv()
app = Flask("researchy-api")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("index.html")

@app.route("/signup")
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else if request.method == "POST":
        return render_template("signup.html")

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
