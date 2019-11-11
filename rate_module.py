from datetime import datetime
import re
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
        fog = fog_index(text)
        updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if status == 1:
            valid = 2
        if status == 2:
            valid = 1

        db.rating.insert_one({'url': url, 'valid': valid, 'fog': fog, 'date': updated})

        return True
    except Exception as e:
        print(e)
        return True


def extract_domain(url):
    parsed_uri = urlparse(url)
    result = '{uri.netloc}'.format(uri=parsed_uri)
    return result


def fog_index(text):
    index = 0
    if sentence_count(text) >= 3:
        try:
            gunning_fog_index =((wordcount(text) / sentence_count(text)) + 100 * (counting(text) / wordcount(text))) * 0.4
            index = gunning_fog_index/4
            if index > 5:
                index = 5
            return index
        except ZeroDivisionError:
            return 0
    else:
        return 0


def wordcount(text):
    # Regex to match all words, hyphenated words count as a compound words
    return len(re.findall("[a-zA-Z-]+", text))


def sentence_count(text):
    sentences = break_sentences(text)
    return len(sentences)


def counting(text):
    syllablecount = 0
    beg_each_Sentence = re.findall(r"\.\s*(\w+)", text)
    capital_words = re.findall(r"\b[A-Z][a-z]+\b", text)
    words = text.split()
    for word in words:
        if word not in capital_words and len(word) >= 3:

            if syllables(word) >= 3 and len(word) == 1:
                syllablecount += 1

        if word in capital_words and word in beg_each_Sentence:

            if syllables(word) >= 3:
                syllablecount += 1
    return syllablecount


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
    data["total"] = ((data["valid"]*2.5) + data["fog"])/2
    data.sort_values("total", inplace=True, ascending=False)

    ratings = pd.DataFrame(data.groupby('url')['total'].mean())
    ratings.sort_values("total", inplace=True, ascending=False)

    updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.ranking.drop()
    for r in ratings['total'].keys():
        db.ranking.insert_one({'url': r, 'rating': ratings['total'][r], 'updated': updated})


def syllables(word):
    word = word.lower()
    word = word + " "  # word extended
    length = len(word)
    ending = ["ing ", "ed ", "es ", "ous ", "tion ", "nce ", "ness "]  # not included in complex words
    vowels = "aeiouy"

    for end in ending:
        x = word.find(end)
        if x > -1:
            x = length - x
            word = word[:-x]
    syllable_count = 0
    if word[-1] == " ":
        word = word[:-1]
    # removing the extra " " at the end if failed and dropping last letter if e
    if word[-1] == "e":
        try :
            if word[-3:] == "nce" and word[-3:] == "rce":
                syllable_count = 0

            elif word[-3] not in vowels and word[-2] not in vowels and word[-3:] != "nce" and word[-3:] != "rce":
                if word[-3] != "'":
                    syllable_count += 1  # e cannot be dropped as it contributes to a syllable
            word = word[:-1]
        except IndexError:
            syllable_count += 0

    one_syllable_beg = ["ya", "ae", "oe", "ea", "yo", "yu", "ye"]
    two_syllables = ["ao", "uo", "ia", "eo", "ea", "uu", "eous", "uou", "ii", "io", "ua", "ya", "yo", "yu", "ye"]
    last_letter = str()  # last letter is null for the first alphabet
    for index, alphabet in enumerate(word):
        if alphabet in vowels:
            current_combo = last_letter + alphabet
            if len(current_combo) == 1:  # if it's the first alphabet
                if word[1] not in vowels:  # followed by a consonant, then one syllable
                    syllable_count += 1
                    last_letter = word[1]
                else:
                    syllable_count += 1  # followed by a vowel
                    last_letter = alphabet

            else:
                if current_combo in two_syllables:
                    try:
                    # if they're only 1 syllable at the beginning of a word, don't increment
                        if current_combo == word[:2] and current_combo in one_syllable_beg:
                            syllable_count += 0
                        elif word[index - 2] + current_combo + word[index + 1] == "tion" or word[index - 2] + current_combo + \
                                word[index + 1] == "sion":  # here io is one syllable :
                            syllable_count += 0

                        else:
                            syllable_count += 1  # vowel combination forming 2 syllables

                        last_letter = alphabet
                    except IndexError:
                        syllable_count += 0

                else:  # two vowels as well as non vowel combination
                    if last_letter not in vowels:
                        syllable_count += 1
                        last_letter = alphabet

                    else:
                        last_letter = alphabet


        else:
            last_letter = alphabet

    if word[-3:] == "ier":  # word ending with ier has 2 syllables
        syllable_count += 1

    return syllable_count