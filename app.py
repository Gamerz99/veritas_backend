from flask_restful import Resource,Api,reqparse
from flask import Flask
import twitter_stream
import time, threading
import json
import keyword_extract
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()


def timer():
    twitter_stream.tweet_crowler()
    threading.Timer(60, timer).start()


class home(Resource):
    def get(self):
        return {"message": "success"}, 200


class check(Resource):

    def post(self):
        result = 0
        tweets = []
        related = []
        rescount = 0

        parser.add_argument('data', type=str, help="add news content", required=True)
        args=parser.parse_args()
        data = args['data']

        if data:
            recent = keyword_extract.extract(data)
            with open('tweets.json') as json_file:
                data = json.load(json_file)
                for d in data['data']:
                    keywords = {'verb': d['keywords']['verb'], 'noun':d['keywords']['noun'], 'adj': d['keywords']['adj'], 'adv': d['keywords']['adv']}
                    tweets.append({'keywords': keywords, 'text': d['text'], 'likes': d['likes'], 'name': d['name'], 'image': d['image'], 'date': d['date']})

            for tweet in tweets:
                threshold = 1
                for count in range(1, 3):
                    if result != 1 and keyword_extract.sentence_match(tweet['keywords']['noun'], recent['noun'], threshold) and keyword_extract.sentence_match(tweet['keywords']['verb'], recent['verb'],threshold):
                        result = count
                        related.append({'text': tweet['text'], 'name': tweet['name'], 'image': tweet['image'], 'date': tweet['date'], 'likes': tweet['likes']})
                        rescount = rescount + 1
                    threshold = 0.5

        response = {"message": "success", "count": rescount, "response": result, "related": related}
        return {"data": response}, 200


class source_pool(Resource):
    def get(self):
        source_list = []

        with open('source_pool.json') as json_file:
            data = json.load(json_file)
            for p in data['pool']:
                source_list.append({"name": p['name'], "screen_name": '@'+p['screen_name'], "image": p['image']})
        return {"message": "success", "response": source_list}, 200


api.add_resource(home, "/")
api.add_resource(check, "/check")
api.add_resource(source_pool, "/source_pool")

if __name__ == "__main__":
    timer()
    app.run()

