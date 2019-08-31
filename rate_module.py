from datetime import datetime
import json
from urllib.parse import urlparse
from textstat.textstat import textstatistics, legacy_round
from nltk.tokenize import PunktSentenceTokenizer

def rate(url, status, text):
    write_data = []
    url = extract_domain(url)
    try:
        smog = smog_index(text)
        with open('rating.json') as json_file:
            data = json.load(json_file)
            for d in data:
                write_data.append({'url': d['url'], 'rating': d['rating'], 'date': d['date'], 'smog': d['smog']})
        with open('rating.json', 'w') as tf:
            updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            write_data.append({'url': url, 'rating': status, 'smog': smog, 'date': updated})
            json.dump(write_data, tf, indent=2)
        tf.close()
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


# Returns the number of sentences in the text
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


