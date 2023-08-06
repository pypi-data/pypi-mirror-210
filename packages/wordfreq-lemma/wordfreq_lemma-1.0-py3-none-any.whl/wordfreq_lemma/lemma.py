import nltk

from collections import defaultdict
from nltk.stem import WordNetLemmatizer
import pkgutil
import json

POS_MAP = {
    "NN": "n",
    "NNS": "n",
    "VB": "v",
    "VBD": "v",
    "VBG": "v",
    "VBN": "v",
    "VBP": "v",
    "VBZ": "v",
    "JJ": "a",
    "JJR": "a",
    "JJS": "a",
    "RB": "r",
    "RBR": "r",
    "WRB": "r",
    "PRP$": "s",
    "WP$": "s",
}


def get_most_common_pos(word):
    tagged_words = nltk.pos_tag([word])
    return POS_MAP.get(tagged_words[0][1], 'n')


def get_lemmatizer():
    nltk.download('brown')
    nltk.download('averaged_perceptron_tagger')
    lemmatizer = WordNetLemmatizer()
    return lambda w: lemmatizer.lemmatize(w, get_most_common_pos(w))


def lemmatized_count(d, lemmatizer):
    counter = defaultdict(int)
    for w, c in d.items():
        lemma = lemmatizer(w)
        counter[lemma] += c
    return counter


class WordUsage:

    def __init__(self):
        nltk.download('brown')
        nltk.download('averaged_perceptron_tagger')
        self.lemmatizer = WordNetLemmatizer()
        datafile = pkgutil.get_data('wordfreq_lemma', 'data/lemma_count.json')
        with open(datafile) as fd:
            self.counter = json.load(fd)

    def freq(self, word):
        pos = get_most_common_pos(word)
        lemma = self.lemmatizer.lemmatize(word, pos)
        return self.counter.get(lemma, 0.0)
