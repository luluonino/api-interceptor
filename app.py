import os
import json
from itertools import combinations
from collections import defaultdict 

from flask import Flask, request, Response
from flask_cors import CORS

from src.proxy import proxy
from src.creds import Creds
from src.postgresHandler import PostgresHandler

path_of_home = os.path.dirname(os.path.realpath(__file__))


passthru = proxy()

application = Flask(__name__)
CORS(application, support_credentials=True)


@application.route("<path-to-api>", methods=["POST"])
def llm_match(*args, **kwargs):

    d = request.data.decode("utf8")
    authToken = json.loads(d)["authToken"]

    if authToken != myCreds.creds["llm_token"]:
        return Response("", 401, {}, "")
    else:
        return passthru(*args, **kwargs)

application.route("/api/<path:path>", methods=["POST", "GET", "PUT", "DELETE"])(passthru)

if __name__ == "__main__":
    application.run(debug=True)
