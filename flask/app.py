from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from datetime import datetime
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
api = Api(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['raw_news']
news_data_collection = db['news_data']
job_log_collection = db['job_log']

logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)


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

        # Query the MongoDB collection
        result = list(news_data_collection.find(query, {"_id": 0}))

        return jsonify(result)


# Add the NewsResource to the API
api.add_resource(NewsResource, '/news')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
