## Reddit Data Pre-processing

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import re
import string
import nltk
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("darkgrid")

r_data = pd.read_csv("/Users/sarwaridas/wallstreetbets/reddit_wsb.csv")
r_data = r_data[pd.to_datetime(r_data.timestamp).dt.year >= 2021]
r_data["text"] = r_data["title"].astype(str) + " " + r_data["body"].astype(str)


# title_data = r_data[['title','timestamp']].copy()
# body_data = r_data[['body','timestamp']].copy()
# body_data = body_data.dropna()
# title_data = title_data.dropna()


# #Remove handlers
r_data.text = r_data.text.apply(lambda x: re.sub("@[^\s]+", "", str(x)))

# Remove URLS
def cleaning_URLs(data):
    return re.sub("((www\.[^\s]+)|(https?://[^\s]+))", " ", data)


r_data.text = r_data.text.apply(lambda x: cleaning_URLs(x))
# Remove all the special characters
r_data.text = r_data.text.apply(lambda x: " ".join(re.findall(r"\w+", str(x))))

# remove all single characters
# r_data.text = r_data.text.apply(lambda x:re.sub(r'\s+[a-zA-Z]\s+', '', str(x)))

# Substituting multiple spaces with single space
r_data.text = r_data.text.apply(lambda x: re.sub(r"\s+", " ", str(x), flags=re.I))

# Remove Time From Timestamp
r_data.timestamp = pd.to_datetime(r_data.timestamp).dt.date

# removing stopwords
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer


stopwords_list = set(stopwords.words("english"))


def cleaning_stopwords(text):
    return " ".join([word for word in str(text).split() if word not in stopwords_list])


r_data.text = r_data.text.apply(lambda x: cleaning_stopwords(x))

st = nltk.PorterStemmer()


def stemming_on_text(data):
    text = [st.stem(word) for word in data]
    return data


r_data.text = r_data.text.apply(lambda x: stemming_on_text(x))

import nltk

nltk.download("wordnet")
from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()


def lemmatizer_on_text(data):
    text = [wnl.lemmatize(word) for word in data]
    return data


r_data.text = r_data.text.apply(lambda x: lemmatizer_on_text(x))

r_data = r_data.drop(
    ["created", "comms_num", "url", "id", "score", "body", "title"], axis=1
)
