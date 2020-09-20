from flask import Flask, render_template, url_for, jsonify, request
from flask_jwt_extended import JWTManager,create_access_token,jwt_required, get_jwt_identity, get_current_user
import uuid
from flask.views import View
from webapp.main.config import DevConfig
from webapp.main.constants import MAX_CONCURRENT_TRANSFORMATIONS, MAX_PAYLOAD_IN_MB
import timeit
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from webapp.main.utils import (is_app_healthy, sort_, scrape)

# Initialize flask app
app = Flask(__name__)
app.config.from_object(DevConfig)
jwt = JWTManager(app)


@app.route("/gettoken", methods=["GET"])
def get_token():
    request_body = request.json
    username = request_body.get("username")
    password = request_body.get("password")
    token = create_access_token(username + " " + password)
    return jsonify({"access_token": token})


# View function for ping

class Ping(View):
    """
    This is a view function for the path /ping.
    Any request to /ping will be handled here
    """

    methods = ['GET']
    decorators = [jwt_required]

    def dispatch_request(self):
        username = get_jwt_identity()
        if not is_app_healthy():
            return jsonify({"message": "Not healthy"}), 500

        return jsonify({"message": f"Application is healthy."}), 200


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
        if is_concurrent.lower() == "false":
            print(" Concurrency value set to false ")
            time_before = timeit.default_timer()
            sorted_list = sort_(input_list)
            time_after = timeit.default_timer()
            time_delta = time_after - time_before
        else:
            with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TRANSFORMATIONS) as executor:
                time_before = timeit.default_timer()
                future_list = executor.submit(sort_, input_list)
                sorted_list = future_list.result()
                time_after = timeit.default_timer()
                time_delta = time_after - time_before
                print(sorted_list, type(sorted_list))

        return jsonify({"time-taken": time_delta, "sorted-list": sorted_list}), 200


class WebCrawl(View):

    methods = ["POST"]

    def dispatch_request(self):

        title_list = list()
        request_body = request.json
        is_parallel = request_body.get("parallel")
        tracker_id = request_body.get("tracker-id")
        url_list = request_body.get("input_list")

        if is_parallel.lower() == "false":
            time_start = timeit.default_timer()
            for url in url_list:
                title = scrape(url)
                title_list.append(str(title))
            time_end = timeit.default_timer()
            time_taken = time_end - time_start
        else:
            with ThreadPoolExecutor(max_workers=4) as executor:
                time_start = timeit.default_timer()
                future_result = executor.map(scrape, url_list)
                for result in future_result:
                    title_list.append(str(result))
                time_end = timeit.default_timer()
                time_taken = time_end - time_start

        return jsonify({"time-taken": time_taken, "sorted_list": title_list}), 200


app.add_url_rule("/ping", view_func=Ping.as_view("ping"))
app.add_url_rule("/execution-parameters", view_func=DefaultConfig.as_view("defaultconfig"))
app.add_url_rule("/sort", view_func=Sort.as_view("sort"))
app.add_url_rule("/web-crawler", view_func=WebCrawl.as_view('webcrawl'))


