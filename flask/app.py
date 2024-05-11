from flask import Flask
from flask_restful import Resource, Api
from config_file import configs as scrape_configs


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
api = Api(app)


configs = {c['name']: c for c in scrape_configs}


class Config(Resource):

    def get(self, platform):

        if platform == "all":
            return {'configs': configs}, 200
        if platform in configs.keys():
            return {'config': configs[platform]}, 200

        return {'config': None}, 404


class RawNews(Resource):

    def get(self, platform):
        return {'data': None}, 404


api.add_resource(Config, '/config/<string:platform>')
api.add_resource(RawNews, '/news/<string:platform>')


if __name__ == '__main__':
    app.run(debug=True)