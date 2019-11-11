from flask_restful import Resource, Api, reqparse
from flask import Flask
import twitter_stream
import time, threading
import json, re
import keyword_extract
import rate_module
from flask_cors import CORS
import web_scrap
import feedback_mod
from datetime import datetime
import sentiment_mod as s
from pymongo import MongoClient


app = Flask(__name__)
CORS(app)
api = Api(app)
client = MongoClient("mongodb://gamerz:gamerz123@cluster0-shard-00-00-tujhc.mongodb.net:27017,cluster0-shard-00-01-tujhc.mongodb.net:27017,cluster0-shard-00-02-tujhc.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.veritas


def timer():
    twitter_stream.tweet_crowler()
    threading.Timer(900, timer).start()


def timer2():
    rate_module.ranking()
    threading.Timer(900, timer2).start()


class Home(Resource):
    def get(self):
        return {"message": "success"}, 200


class Check(Resource):

    def post(self):
        result = 0
        tweets = []
        related = []
        rescount = 0
        url = ''
        url_base = False
        check = ''
        rvalue = 0.2

        parser = reqparse.RequestParser()
        parser.add_argument('data', type=str, help="add news content", required=True)
        args = parser.parse_args()
        data = args['data']

        if data:
            try:
                check = re.search("(?P<url>https?://[^\s]+)", data).group("url")
            except BaseException as e:
                check = ''
            if check != '':
                url = data
            if url != '':
                article = web_scrap.getArticle(url)
                recent = web_scrap.getkeywords(article)
                url_base = True
            if url == '':
                recent = keyword_extract.extract(data)
                url_base = False

            if url_base:
                resentiment = s.sentiment(data)
                print("Input text : ", data, " --- sentiment value : ", resentiment[0])
                rvalue = 0.13
            tweets = db.tweets.find({})

            for tweet in tweets:
                try:
                    ratio1 = keyword_extract.sentence_match(tweet['keywords']['noun'], recent['noun'])
                    ratio2 = keyword_extract.sentence_match(tweet['keywords']['verb'], recent['verb'])
                except BaseException as e:
                    ratio2 = 0
                    ratio1 = 0

                if ratio1 == 1 and ratio2 == 1:
                    print("Related tweets : ", tweet['text'], " --- sentiment value : ", tweet['sentiment'])
                    result = 1
                    related.append(
                        {'text': tweet['text'], 'name': tweet['name'], 'image': tweet['image'], 'date': tweet['date'],
                         'likes': tweet['likes'], 'updated': tweet['updated']})
                    rescount = rescount + 1

                elif ratio1 >= rvalue and ratio2 >= 0:
                    if url_base:
                        print("Related tweets : ", tweet['text'], " --- sentiment value : ", tweet['sentiment'])
                        if resentiment[0] == tweet['sentiment']:
                            if result != 1:
                                result = 2
                            related.append(
                                {'text': tweet['text'], 'name': tweet['name'], 'image': tweet['image'], 'date': tweet['date'],
                                 'likes': tweet['likes'], 'updated': tweet['updated']})
                            rescount = rescount + 1
                    else:
                        if result != 1:
                            result = 2
                        related.append(
                            {'text': tweet['text'], 'name': tweet['name'], 'image': tweet['image'],
                             'date': tweet['date'],
                             'likes': tweet['likes'], 'updated': tweet['updated']})
                        rescount = rescount + 1

            if url_base:
                rate_module.rate(url, result, article)

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


class RankingList(Resource):
    def get(self):
        ranking_list = []

        data = db.ranking.find({})
        for p in data:
            ranking_list.append({"url": p['url'], "rating": +p['rating'], "updated": p['updated']})

        return {"message": "success", "response": ranking_list}, 200


class Feedback(Resource):
    def post(self):

        check = "good"
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help="add email", required=True)
        parser.add_argument('name', type=str, help="add name", required=True)
        parser.add_argument('subject', type=str, help="add subject", required=True)
        parser.add_argument('comment', type=str, help="add comment", required=True)
        args = parser.parse_args()
        name = args['name']
        email = args['email']
        subject = args['subject']
        comment = args['comment']

        if name:
            try:
                check = feedback_mod.check_spam(comment)
                print(check)
                if check == "good":
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    db.feedback.insert_one({'name': name, 'email': email, 'subject': subject, 'comment': comment, 'date': date})

                return {"message": "success", "response": check}, 200

            except Exception as e:
                print(e)
                return {"message": "fail"}, 404

    def get(self):
        feedback_list = []

        data = db.feedback.find({})
        for p in data:
            feedback_list.append({"name": p['name'], "email": p['email'], "subject": p['subject'], "comment": p['comment'], "date": p['date']})

        return {"message": "success", "response": feedback_list}, 200


api.add_resource(Home, "/")
api.add_resource(Check, "/check")
api.add_resource(SourcePool, "/source_pool")
api.add_resource(RankingList, "/ranking_list")
api.add_resource(Feedback, "/feedback")

if __name__ == "__main__":
    #timer()
    # timer2()
    app.run()






