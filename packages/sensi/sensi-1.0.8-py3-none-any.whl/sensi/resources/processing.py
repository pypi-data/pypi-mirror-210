import os
import re
from typing import List

from bahasa.stemmer import Stemmer
import nltk
from nltk.tokenize import word_tokenize

from sensi.database.query import read_stop_words

pwd = os.path.dirname(os.path.realpath(__file__))
nltk_path = f"{pwd}/nltk_data"
nltk.data.path.append(nltk_path)


def rem_stop(txt) -> list:
    """Remove stop words"""
    # return list(readStopWords())
    return [t for t in txt if t not in list(read_stop_words())]


def normalisasi(txt: str) -> List[str]:
    """Text normalization or Pre-processing"""
    # * stemming
    stemmer = Stemmer()
    txt = stemmer.stem(txt)
    # * remove urls
    txt = re.sub(r"http\S+", " ", txt)
    # * remove punctuations
    txt = re.sub(r"[^\w\s]", " ", txt)
    # * remove numbers
    txt = re.sub(r"\d+", " ", txt)
    # * tokenize string
    txt = word_tokenize(txt)  # type: ignore
    # * remove stop words, return normalized strings in a list
    return rem_stop(txt)


def freqs(txt: str) -> List[tuple]:
    """Determine unique word's frequencies
    Output: tuple
    """
    return nltk.FreqDist(txt).most_common()
