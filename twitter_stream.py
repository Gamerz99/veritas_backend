from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from datetime import datetime, timedelta, timezone

import json
import credintials
import keyword_extract
from pymongo import MongoClient
import sentiment_mod as s

client = MongoClient("mongodb://gamerz:gamerz123@cluster0-shard-00-00-tujhc.mongodb.net:27017,cluster0-shard-00-01-tujhc.mongodb.net:27017,cluster0-shard-00-02-tujhc.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.veritas


# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

    def get_twitter_client_api(self):
            return self.twitter_client

    def get_user_timeline_tweets(self, twitter_source, num_tweets):

        startDate = datetime.now() - timedelta(hours=90)
        tweets = []
        for source in twitter_source:
            for tweet in Cursor(self.twitter_client.user_timeline, screen_name=source, tweet_mode='extended').items(num_tweets):
                if tweet.created_at > startDate:
                    tweets.append(tweet)
        return tweets


# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(credintials.CONSUMER_KEY, credintials.CONSUMER_KEY_SECREAT)
        auth.set_access_token(credintials.ACCESS_TOKEN, credintials.ACCESS_TOKEN_SECREAT)
        return auth


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """
    def tweets_to_json(self, tweets):
        try:
            db.tweets.drop()
            for tweet in tweets:
                twsentiment = s.sentiment(tweet.full_text)
                updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                date = utc_to_local(tweet.created_at).strftime('%Y-%m-%d %H:%M:%S')
                write_data = {'id': tweet.id, 'name': tweet.user.name, 'screen_name': tweet.user.screen_name, 'image': tweet.user.profile_image_url, 'text': tweet.full_text, 'length': len(tweet.full_text), 'likes': tweet.favorite_count, 'retweet': tweet.retweet_count, 'keywords': keyword_extract.extract(tweet.full_text), 'verified': tweet.user.verified, 'sentiment': twsentiment[0], 'date': date, 'updated': updated}
                db.tweets.insert_one(write_data)
            print("successfully")
            return True
        except BaseException as e:
            print (e)
            return True


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def tweet_crowler():
    source_list = []

    with open('source_pool.json') as json_file:
        data = json.load(json_file)
        for p in data['pool']:
            source_list.append(p['screen_name'])

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    tweets = twitter_client.get_user_timeline_tweets(source_list, 50)
    tweet_analyzer.tweets_to_json(tweets)

