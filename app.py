from flask import Flask, request, make_response
from flask_restful import Resource, Api
from modules.website import Website

app = Flask("researchy-api")
api = Api(app)


class ResearchyAPI(Resource):
    def post(self):
        body = request.form
        print(body)
        if not body:
            return make_response("Please provide a JSON object.", 400)
        if "text" not in body and "url" not in body:
            return make_response("Please provide a text or url.", 400)
        display = Website(
            url=body.get("url", None), raw_html=body.get("text", None)
        )
        return make_response(display.description, 200)


api.add_resource(ResearchyAPI, "/")

# running on https://researchy-api--kevinlu2.repl.co

if __name__ == "__main__":
    app.run(debug=False, port=5001)
