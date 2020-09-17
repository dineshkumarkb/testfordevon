from flask import Flask, render_template, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager,create_access_token,jwt_required, get_jwt_identity, get_current_user
import uuid
from flask.views import View
from constants import MAX_CONCURRENT_TRANSFORMATIONS, MAX_PAYLOAD_IN_MB
import time, timeit
from bs4 import BeautifulSoup
from urllib import request as urlrequest

# Initialize flask app
app = Flask(__name__)


# View function for ping
class Ping(View):
    """
    This is a view function for the path /ping.
    Any request to /ping will be handled here
    """

    methods = ['GET']

    def dispatch_request(self):

        if not is_app_healthy():
            return jsonify({"message": "Not healthy"}), 500

        return jsonify({"message": "Hi There"}), 200


class DefaultConfig(View):

    methods = ["GET"]

    def dispatch_request(self):

        return jsonify({'MaxConcurrentTransformations': MAX_CONCURRENT_TRANSFORMATIONS,
                        'MaxPayloadInMB': MAX_PAYLOAD_IN_MB}), 200


class Sort(View):

    methods = ["POST"]

    def dispatch_request(self):
        print(f"Received body {request.json}")
        is_concurrent = request.json.get("concurrent")
        input_list = request.json.get("input_list")
        time_before = timeit.default_timer()
        sorted_list = sorted(input_list)
        time_after = timeit.default_timer()
        time_delta = time_after - time_before
        print(time_delta)
        print(type(time.time()))
        return jsonify({"time-taken": time_delta, "sorted-list": sorted_list}), 200


class WebCrawl(View):

    methods = ["POST"]

    def dispatch_request(self):

        request_body = request.json
        is_parallel = request_body.get("parallel")
        tracker_id = request_body.get("tracker-id")
        input_list = request_body.get("input_list")
        url = "https://www.google.com"
        html = urlrequest.urlopen(url).read().decode('utf-8')
        html[:60]
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find('title')
        print(title)
        return jsonify("Received request"), 200



def is_app_healthy():
    """
    """
    return True


if __name__ == "__main__":
    app.add_url_rule("/ping", view_func=Ping.as_view("ping"))
    app.add_url_rule("/execution-parameters", view_func=DefaultConfig.as_view("defaultconfig"))
    app.add_url_rule("/sort", view_func=Sort.as_view("sort"))
    app.add_url_rule("/web-crawler", view_func=WebCrawl.as_view('webcrawl'))
    app.run(debug=True)
