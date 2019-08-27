from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
from datetime import datetime, timedelta, timezone

import os
import json
import credintials
import numpy as np
import pandas as pd
import keyword_extract


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


# # # # TWITTER STREAMER # # # #
class TweetsStreamer ():

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets , hash_tags):
        listener = TweeterListener(fetched_tweets)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track=hash_tags)


# # # # TWITTER STREAM LISTENER # # # #
class TweeterListener (StreamListener):

    def __init__(self, fetched_tweets):
        self.fetched_tweets = fetched_tweets

    def on_data(self, raw_data):
        try:
            print (raw_data)
            with open(self.fetched_tweets,'a') as tf:
                tf.write(raw_data)
            return True
        except BaseException as e:
            print (e)
            return True

    def on_error(self, status_code):
        if status_code == 420:
            return False
        print (status_code)


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """
    def __init__(self, fetched_tweets):
        self.fetched_tweets = fetched_tweets

    def tweets_to_data_frame(self, tweets):
        keywords = []
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
        for t in tweets:
            keywords.append(keyword_extract.extract(t.text))

        df['keywords'] = keywords
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])

        return df

    def tweets_to_json(self, tweets):
        write_data = {}
        write_data = ""

        if os.path.exists("tweets.json"):
            os.remove("tweets.json")

        try:
            with open(self.fetched_tweets, 'w') as tf:
                for tweet in tweets:
                    updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    date = utc_to_local(tweet.created_at).strftime('%Y-%m-%d %H:%M:%S')
                    write_data['data'].append({'id': tweet.id, 'name': tweet.user.name, 'screen_name': tweet.user.screen_name, 'image': tweet.user.profile_image_url, 'text': tweet.full_text, 'length': len(tweet.full_text), 'likes': tweet.favorite_count, 'retweet': tweet.retweet_count, 'keywords': keyword_extract.extract(tweet.full_text), 'verified': tweet.user.verified, 'date': date, 'updated': updated})
                json.dump(write_data, tf, indent=2)
            tf.close()
            print("ss")
            return True
        except BaseException as e:
            print (e)
            return True


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def search_hashtags():
    df = pd.DataFrame(columns=['text'])
    msgs = []
    msg = []

    for tweet in Cursor(api.search, q=hash_tags, rpp=100).items(10):
        msg = [tweet.text]
        msg = tuple(msg)
        msgs.append(msg)

    df = pd.DataFrame(msgs)
    print(df.head(10))


def tweet_crowler():
    fetched_tweets = "tweets.json"
    source_list = []

    with open('source_pool.json') as json_file:
        data = json.load(json_file)
        for p in data['pool']:
            source_list.append(p['screen_name'])

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer(fetched_tweets)

    tweets = twitter_client.get_user_timeline_tweets(source_list, 50)
    tweet_analyzer.tweets_to_json(tweets)


if __name__ == '__main__':
    hash_tags =['barack obama']
    fetched_tweets = "tweets.json"
    source_list = ['cnnbrk','BBCBreaking']

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer(fetched_tweets)
    api = twitter_client.get_twitter_client_api()

    tweet_crowler()

    # tweets = twitter_client.get_user_timeline_tweets(source_list, 50)
    # tweet_analyzer.tweets_to_json(tweets)

    #df = tweet_analyzer.tweets_to_data_frame(tweets)
    #print(df.head(20))

    #streamer = TweetsStreamer()
    #streamer.stream_tweets(fetched_tweets, hash_tags)

    #search_hashtags()