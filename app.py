from flask_restful import Resource,Api,reqparse
from flask import Flask
import twitter_stream
import time, threading
import json
import keyword_extract
import rate_module
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)
parser = reqparse.RequestParser()


def timer():
    twitter_stream.tweet_crowler()
    threading.Timer(120, timer).start()


class Home(Resource):
    def get(self):
        return {"message": "success"}, 200


class Check(Resource):

    def post(self):
        result = 0
        tweets = []
        related = []
        rescount = 0
        url_base = False

        parser.add_argument('data', type=str, help="add news content", required=True)
        args=parser.parse_args()
        data = args['data']

        if data:
            recent = keyword_extract.extract(data)
            with open('tweets.json') as json_file:
                data = json.load(json_file)
                for d in data['data']:
                    keywords = {'verb': d['keywords']['verb'], 'noun':d['keywords']['noun'], 'adj': d['keywords']['adj'], 'adv': d['keywords']['adv']}
                    tweets.append({'keywords': keywords, 'text': d['text'], 'likes': d['likes'], 'name': d['name'], 'image': d['image'], 'date': d['date'], 'updated': d['updated']})

            for tweet in tweets:
                threshold = 1
                for count in range(1, 3):
                    if result != 1 and keyword_extract.sentence_match(tweet['keywords']['noun'], recent['noun'], threshold) and keyword_extract.sentence_match(tweet['keywords']['verb'], recent['verb'],threshold):
                        result = count
                        related.append({'text': tweet['text'], 'name': tweet['name'], 'image': tweet['image'], 'date': tweet['date'], 'likes': tweet['likes'],  'updated': tweet['updated']})
                        rescount = rescount + 1
                    threshold = 0.5
            if url_base:
                rate_module.rate('https://bbc.com/questions/9626535/get-protocol-host-name-from-url', result)

        response = {"message": "success", "count": rescount, "response": result, "related": related}
        return {"data": response}, 200


class SourcePool(Resource):
    def get(self):
        source_list = []

        with open('source_pool.json') as json_file:
            data = json.load(json_file)
            for p in data['pool']:
                source_list.append({"name": p['name'], "screen_name": '@'+p['screen_name'], "image": p['image']})
        return {"message": "success", "response": source_list}, 200


api.add_resource(Home, "/")
api.add_resource(Check, "/check")
api.add_resource(SourcePool, "/source_pool")

if __name__ == "__main__":
    app.run()




