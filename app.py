from flask import Flask
from flask import make_response
from flask import render_template
from flask import request

from modules.website import Website
# from flask_restful import Resource, Api

app = Flask("researchy-api")


@app.route("/")
def index():
    return render_template("index.html")


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


# api = Api(app)

# class ResearchyAPI(Resource):
#     def get(self):
#         # Placeholder
#         return render_template("index.html")

# def post(self):
#     body = request.form
#     print(body)
#     if not body:
#         return make_response("Please provide a JSON object.", 400)
#     if "text" not in body and "url" not in body:
#         return make_response("Please provide a text or url.", 400)
#     display = Website(url=body.get("url", None), raw_html=body.get("text", None))
#     return make_response(display.description, 200)


# api.add_resource(ResearchyAPI, "/")

# running on https://researchy-api.herokuapp.com
# running on http://64.225.115.179/

if __name__ == "__main__":
    app.run(debug=False, port=5001)
