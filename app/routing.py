from operator import itemgetter

from app.db import *
from modules.website import Website


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


@app.route("/storage", methods=["POST"])
def storage():
    body = request.json
    try:
        email, gaia_id, storage = itemgetter("email", "id", "data")(body)
    except KeyError as error:
        return make_response("Key not found error: {}".format(error), 400)
    try:
        File.handleStorage(email, gaia_id, storage)
        db.session.commit()
    except AssertionError as error:
        return make_response(str(error), 400)
    else:
        return make_response("Success", 200)


# running on https://researchy-api.herokuapp.com
# running on http://64.225.115.179/

if __name__ == "__main__":
    app.run(debug=False, port=5001)
