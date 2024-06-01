from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from datetime import datetime
import logging
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')
api = Api(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['raw_news']
news_data_collection = db['news_data']
comments_collection = db['comments']
job_log_collection = db['job_log']


def get_logger(is_file=False, is_console=False):

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the minimum log level

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    if is_file:
        # Create a file handler for output file
        file_handler = logging.FileHandler('flask_app.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if is_console:
        # Create a console handler for output to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


@app.before_request
def log_request_info():
    request.start_time = datetime.now()
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request body: {request.get_data()}")


@app.after_request
def log_response_info(response):
    duration = datetime.now() - request.start_time
    logger.info(f"Response status: {response.status}")
    logger.info(f"Request took {duration.total_seconds():.4f} seconds")
    logger.debug(f"Response headers: {response.headers}")
    # logger.debug(f"Response body: {response.get_data()}")
    return response


class NewsResource(Resource):
    def get(self):
        """
        GET endpoint to query news data.
        Accepts query parameters to filter the results.
        """
        query_params = request.args.to_dict()

        # Initialize the MongoDB query
        query = {}

        # Handle datetime filtering for scrapetime
        if 'before_datetime' in query_params:
            before_datetime = datetime.strptime(query_params['before_datetime'], "%Y-%m-%d %H:%M")
            query['scrapetime'] = {"$lt": before_datetime}

        if 'after_datetime' in query_params:
            after_datetime = datetime.strptime(query_params['after_datetime'], "%Y-%m-%d %H:%M")
            query['scrapetime'] = {"$gt": after_datetime}

        if 'start_datetime' in query_params and 'end_datetime' in query_params:
            start_datetime = datetime.strptime(query_params['start_datetime'], "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(query_params['end_datetime'], "%Y-%m-%d %H:%M")
            query['scrapetime'] = {
                "$gte": start_datetime,
                "$lte": end_datetime
            }

        if 'platform' in query_params:
            query['platform'] = query_params['platform']

        # Query the MongoDB collection
        result = list(news_data_collection.find(query, {"_id": 0}))

        return jsonify(result)


class CommentsResource(Resource):
    def get(self):
        """
        GET endpoint to query news data.
        Accepts query parameters to filter the results.
        """
        query_params = request.args.to_dict()

        # Initialize the MongoDB query
        query = {}

        if 'targetUrl' in query_params:
            target_urls = query_params.getlist('targetUrl')
            query['targetUrl'] = {"$in": target_urls}

        if 'platform' in query_params:
            query['platform'] = query_params['platform']

        # Query the MongoDB collection
        result = list(comments_collection.find(query, {"_id": 0}))

        return jsonify(result)


# Add the NewsResource to the API
api.add_resource(NewsResource, '/news')
api.add_resource(CommentsResource, '/comments')


logger = get_logger(is_file=False, is_console=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
