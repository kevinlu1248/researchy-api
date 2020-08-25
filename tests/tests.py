# !utf-8
# from requests import get
# from modules import *

if __name__ == "__main__":
    # from google.oauth2 import id_token
    # from google.auth.transport import requests

    # # (Receive token by HTTPS POST)
    # # ...

    # token = "ya29.a0AfH6SMCJhCqwK4sY9nr1REB_kTNNsMC6k7mf5kotCLv4DZw_fF44quXnXw7ofIxgaSkhInxZOPGYedjw6Dj8_le7D_wrX30o9HtcLM_0LMmpW5SXBQJGe4aB_L0SveF0_0mjipGnrzW3U5qAaLKG0irtJCouWHQ9EJY"
    # CLIENT_ID = "998017231527-143kulv2us66bg4p3p631cuokrilf5b2.apps.googleusercontent.com"

    # try:
    #     # Specify the CLIENT_ID of the app that accesses the backend:
    #     idinfo = id_token.verify_token(token, requests.Request())

    #     # Or, if multiple clients access the backend server:
    #     # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    #     # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     #     raise ValueError('Could not verify audience.')

    #     # If auth request is from a G Suite domain:
    #     # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
    #     #     raise ValueError('Wrong hosted domain.')

    #     # ID token is valid. Get the user's Google Account ID from the decoded token.
    #     userid = idinfo['sub']
    #     print(userid)
    # except ValueError as e:
    #     # Invalid token
    #     print(e)

    import google.auth.transport.requests
    import google.oauth2.id_token

    request = google.auth.transport.requests.Request()
    target_audience = "https://pubsub.googleapis.com"

    id_token = google.oauth2.id_token.fetch_id_token(request, target_audience)
