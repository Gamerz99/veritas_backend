from nltk.tokenize import TweetTokenizer
import nltk.corpus
import nltk.stem.snowball
from nltk.corpus import wordnet
import nltk
import string, re
import twitter_stream
import rate_module


def get_wordnet_pos(pos_tag):

    if pos_tag[1].startswith('J'):
        return (pos_tag[0], wordnet.ADJ)
    elif pos_tag[1].startswith('V'):
        return (pos_tag[0], wordnet.VERB)
    elif pos_tag[1].startswith('N'):
        return (pos_tag[0], wordnet.NOUN)
    elif pos_tag[1].startswith('R'):
        return (pos_tag[0], wordnet.ADV)
    else:
        return (pos_tag[0], wordnet.NOUN)


def sentence_match(lemmae_a, lemmae_b):

    # Calculate Jaccard similarity
    ratio = len(set(lemmae_a).intersection(lemmae_b)) / float(len(set(lemmae_a).union(lemmae_b)))
    return ratio


def extract(news):

    tokenizer = TweetTokenizer()
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(string.punctuation)
    stopwords.append('')

    news = remove_url(news)
    pos_a = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(news)))
    pos_b = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(news)))
    pos_c = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(news)))
    pos_d = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(news)))
    res = {'noun': [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a
                    if pos == wordnet.NOUN and token.lower().strip(string.punctuation) not in stopwords],
            'verb': [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b
                    if pos == wordnet.VERB and token.lower().strip(string.punctuation) not in stopwords],
            'adj': [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_c
                    if pos == wordnet.ADJ and token.lower().strip(string.punctuation) not in stopwords],
            'adv': [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_d
                    if pos == wordnet.ADV and token.lower().strip(string.punctuation) not in stopwords],
            }
    return res


def remove_url(sample):
    """Remove URLs from a sample string"""
    return re.sub(r"http\S+", "", sample)


if __name__ == '__main__':
    tokenizer = TweetTokenizer()
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(string.punctuation)
    stopwords.append('')

    news = "At least 40 people were killed and 80 injured after an airstrike hit a migrant center east of the Libyan capital of Tripoli, according to the Health Ministry's emergency service Field Medicine and Support Center"
    news2 = "At least 40 people were killed and 80 injured after an airstrike hit a migrant center east of the Libyan capital of Tripoli, according to the Health Ministry's emergency service Field Medicine and Support Center"

    words = tokenizer.tokenize(news)
    words = [word.lower() for word in words if word.isalpha()]

    filtered_sentence = [w for w in words if w not in stopwords]

    #print(sentence_match(news, news2))

    #print(filtered_sentence)

    #for x in filtered_sentence:
        #print(ps.stem(x))
        #print(x)

    #tagging()

    # print(s.sentiment("If they're not showing, I'll just have to resort to their live ticker. At least it's better than hearing 2nd hand news."))
    # print(s.sentiment("I'm awake right now! Gonna travel a few hundred kilometres tomorrow!"))
    # print(s.sentiment("The one day i really need to go into school and i'm not well"))
    # print(s.sentiment("right then nsb archive done and dusted, ape accounts up to date, freeland winner sorted.. haha now to do some real work"))

    #twitter_stream.tweet_crowler()
    rate_module.ranking()
