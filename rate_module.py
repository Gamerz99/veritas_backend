from datetime import datetime
import json
from urllib.parse import urlparse
from textstat.textstat import textstatistics, legacy_round
from nltk.tokenize import PunktSentenceTokenizer
import pandas as pd
from pymongo import MongoClient


client = MongoClient("mongodb://gamerz:gamerz123@cluster0-shard-00-00-tujhc.mongodb.net:27017,cluster0-shard-00-01-tujhc.mongodb.net:27017,cluster0-shard-00-02-tujhc.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.veritas


def rate(url, status, text):
    valid = 0
    url = extract_domain(url)
    try:
        smog = smog_index(text)
        updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if status == 1:
            valid = 2
        if status == 2:
            valid = 1

        db.rating.insert_one({'url': url, 'valid': valid, 'smog': smog, 'date': updated})

        return True
    except Exception as e:
        print(e)
        return True


def extract_domain(url):
    parsed_uri = urlparse(url)
    result = '{uri.netloc}'.format(uri=parsed_uri)
    return result


def smog_index(text):
    if sentence_count(text) >= 3:
        poly_syllab = poly_syllable_count(text)
        SMOG = (1.043 * (30 * (poly_syllab / sentence_count(text))) ** 0.5) \
               + 3.1291
        return legacy_round(SMOG, 1)
    else:
        return 0


def sentence_count(text):
    sentences = break_sentences(text)
    return len(sentences)


def break_sentences(text):
    tokenize = PunktSentenceTokenizer()
    doc = tokenize.tokenize(text)
    return doc


def poly_syllable_count(text):
    count = 0
    words = []
    sentences = break_sentences(text)
    for sentence in sentences:
        words += [token for token in sentence]

    for word in words:
        syllable_count = syllables_count(word)
        if syllable_count >= 3:
            count += 1
    return count


def syllables_count(word):
    return textstatistics().syllable_count(word)


def ranking():
    rate_list = db.rating.find({})
    data = pd.DataFrame(list(rate_list))
    data["total"] = (data["valid"]*5) + data["smog"]
    data["rating"] = data["total"].rank()
    data.sort_values("rating", inplace=True, ascending=False)

    ratings = pd.DataFrame(data.groupby('url')['rating'].mean())
    ratings.sort_values("rating", inplace=True, ascending=False)

    updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.ranking.drop()
    for r in ratings['rating'].keys():
        db.ranking.insert_one({'url': r, 'rating': ratings['rating'][r], 'updated': updated})

