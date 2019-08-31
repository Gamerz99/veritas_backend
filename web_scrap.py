import mechanize
import nltk
import keyword_extract
from bs4 import BeautifulSoup
import string
from nltk.corpus import wordnet


def getHtmlText(url):
    br = mechanize.Browser()
    htmltext = br.open(url).read()
    return htmltext


def getHtmlFile(url):
    br = mechanize.Browser()
    htmlfile = br.open(url)
    return htmlfile


def getArticleText(webtext):
    articletext = ""
    soup = BeautifulSoup(webtext, features="html5lib")
    for tag in soup.findAll("p"):  # ("p", {"class":"css-exrw3m evys1bk0"}):
        articletext += tag.get_text()
    return articletext  # print (tag.get_text()) # get the text without p tag


def getArticle(url):
    htmltext = getHtmlText(url)
    return getArticleText(htmltext)


def getkeywords(articletext):
    result = []
    common = open("common.txt").read().split('\n')
    word_dict = {}
    word_list = articletext.lower().split()
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

    for word in word_list:
        if word not in common and word.isalnum():
            if word not in word_dict:
                word_dict[word] = 1
            if word in word_dict:
                word_dict[word] += 1
    # print (word_dict)
    words = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)[0:20]

    for w in words:
        result.append(w[0])

    pos_a = map(keyword_extract.get_wordnet_pos, nltk.pos_tag(result))
    pos_b = map(keyword_extract.get_wordnet_pos, nltk.pos_tag(result))

    res = {'noun': [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a
                    if pos == wordnet.NOUN and token.lower().strip(string.punctuation)],
           'verb': [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b
                    if pos == wordnet.VERB and token.lower().strip(string.punctuation)]
           }
    return res
