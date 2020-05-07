from flask import Flask, request, make_response
from flask_restful import Resource, Api
from modules.website import Website

app = Flask('researchy-api')
api = Api(app)


class ResearchyAPI(Resource):
    def post(self):
        json_body = request.json
        if not json_body:
            return make_response('Please provide a JSON object.', 400)
        if "text" not in json_body and "url" not in json_body:
            return make_response('Please provide a text or url.', 400)
        display = Website(url=json_body.get('url', None),
                          raw_html=json_body.get('text', None))
        return make_response(str(display.annotated_tree), 200)


api.add_resource(ResearchyAPI, '/')

# @app.route('/', methods=["POST"])
# def index():
#     request_body = app.current_request.json_body
#     # print(request_body)
#     if "text" not in request_body and "url" not in request_body:
#         return Response(status_code=422,
#                         headers={'Content-Type': 'application/json'},
#                         body={'status': 'Entity Error',
#                               'message': 'Please provide a text or url file.'})
#     display = Website(url=request_body.get('url', None),
#                       raw_html=request_body.get('text', None))
#     return Response(status_code=200,
#                     headers={'Content-Type': 'application/json'},
#                     body={'status': 'Success',
#                           'message': str(display.annotated_tree)})

# running on https://researchy-api--kevinlu2.repl.co

if __name__ == '__main__':
    app.run(debug=False)
