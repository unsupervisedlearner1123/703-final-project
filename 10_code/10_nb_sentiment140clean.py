# -*- coding: utf-8 -*-
"""IDS_703_NB_Sentiment140Clean.ipynb

Automatically generated by Colaboratory.
"""

from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

# Importing all required libraries
import pandas as pd
import numpy as np
import pickle
from typing import List
import random
import io
from statistics import mean

from sklearn.model_selection import (
    train_test_split,
    KFold,
    cross_val_score,
    GridSearchCV,
)
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# Fetching stopwords
nltk.download("stopwords")


# Reading in data
# df = pd.read_csv(io.StringIO(uploaded["CLEANED_FOR_REAL.csv"].decode("latin-1")))
# df = pd.read_csv("/content/CLEANED_FOR_REAL.csv", encoding="latin-1")
df = pd.read_csv("./20_intermediate_files/CLEANED_FOR_REAL.csv", encoding="latin-1")
df.head()

# Checking attributes in the dataset
df.info()

# Checking the labels attribute
df["label"].describe()

# Checking for nulls
df.isna().sum() / len(df)

# Drop nulls as they are only 0.4%
df.dropna(axis=0, inplace=True)

# Verifying for nulls again
df.isna().sum() / len(df)

# df["text"] = df["text"].str.lower()
x = df["text"]
y = df["label"]

# Splitting into 75-25 train-test
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.25, random_state=42
)

x_train.shape
y_train.shape

x_test.shape
y_test.shape

token = RegexpTokenizer(r"[a-zA-Z0-9]+")

# Encoding as unicode as there are some special chars in tweets
x_train = x_train.values.astype("U")

# Building the pipeline for NB
classifier = Pipeline(
    [
        ("tfidf", TfidfVectorizer(tokenizer=token.tokenize)),
        ("clf", MultinomialNB()),
    ]
)

tuning_parameters = {
    "tfidf__ngram_range": [(1, 1), (1, 2)],
    "tfidf__use_idf": (True, False),
    "tfidf__smooth_idf": (True, False),
    "tfidf__norm": ("l1", "l2"),
    "tfidf__max_features": (10000, 25000),
    "clf__alpha": [0.1, 0.5, 1, 1.5, 2],
}

# Performing grid search
clf2 = GridSearchCV(classifier, tuning_parameters, verbose=1, cv=10)
clf2.fit(x_train, y_train)

print(classification_report(y_test, clf2.predict(x_test), digits=4))

# Fetch the best parameters correponding to every run
best_parameters = clf2.best_estimator_.get_params()
for param_name in sorted(tuning_parameters.keys()):
    print("\t%s: %r" % (param_name, best_parameters[param_name]))


"""Using Optimal model from Grid Search"""
vec = TfidfVectorizer(
    ngram_range=(1, 2),
    use_idf=False,
    smooth_idf=True,
    max_features=25000,
    norm="l1",
    tokenizer=token.tokenize,
)
x_train_tfidf = vec.fit_transform(x_train)
clf = MultinomialNB(alpha=0.5).fit(x_train_tfidf, y_train)

x_test_tfidf = vec.transform(x_test)
predictions = clf.predict(x_test_tfidf)
predictions_prob = clf.predict_log_proba(x_test_tfidf)

k_fold = KFold(n_splits=10, shuffle=True, random_state=42)
x_tfidf = vec.fit_transform(x.values.astype("U"))
print(
    "Cross Validation score:",
    cross_val_score(clf, x_tfidf, y, cv=k_fold, n_jobs=-1, error_score="raise"),
)

print("Train accuracy ={:.2f}%".format(clf.score(x_train_tfidf, y_train) * 100))
print("Test accuracy ={:.2f}%".format(clf.score(x_test_tfidf, y_test) * 100))

print("Precision score: ", precision_score(y_test, predictions, average="weighted"))
print("Recall score: ", recall_score(y_test, predictions, average="weighted"))

print(classification_report(y_test, predictions, digits=4))

# Generating synthetic data from NB
# Creating the vocabulary frequency matrix
vocab_freq = pd.DataFrame(x_train_tfidf.toarray(), columns=vec.get_feature_names_out())

# Fetching probability of features given label
prob = clf.feature_log_prob_
prob_labels = pd.DataFrame(data=prob, index=clf.classes_)
prob_labels.shape

vocabulary = vocab_freq.columns.values.tolist()

# Checking the average length of a tweet in train sample
nltk.download("punkt")
len_ls = []
for i in df["text"]:
    ls = word_tokenize(i)
    length = len(ls)
    len_ls.append(length)
mean(len_ls)
# Average length of ~7 words


def create_synthetic_tweet(voc: List[str], prob: np.ndarray) -> List[str]:
    words = []
    docs = []
    idx = int(np.random.randint(2, size=1))
    docs.append(prob_labels.index[idx])
    word_proportions = np.random.multinomial(2000, np.exp(prob[idx]))
    for _ in range(7):  # using average of 7 unigrams and/or bigrams
        words.append(random.choices(voc, word_proportions)[0])
    return words, docs


synthetic_tweets = [create_synthetic_tweet(vocabulary, prob) for _ in range(2000)]

synth_labels_ls = ["".join(str(i[1][0])) for i in synthetic_tweets]
synth_tweets_ls = [" ".join(i[0]) for i in synthetic_tweets]

synthetic_df = pd.DataFrame(data={"labels": synth_labels_ls, "tweets": synth_tweets_ls})
synthetic_df.head()

# Saving file
synthetic_df.to_csv("./20_intermediate_files/Synthetic_from_NB.csv", index=False)

# Saving vectorizer and classifier
f = open("NB_classifier.pickle", "wb")
pickle.dump(clf, f)
f.close()

f = open("NB_vectorizer.pickle", "wb")
pickle.dump(vec, f)
f.close()

"""Testing on synthetic data"""

# Loading saved vectorizer and classifier
f = open("/content/NB_vectorizer.pickle", "rb")
vec = pickle.load(f)
f.close()

f = open("/content/NB_classifier.pickle", "rb")
clf = pickle.load(f)
f.close()

# Reading in synthetic data
# df_synth = pd.read_csv(
#     io.StringIO(uploaded2["Synthetic_from_NB.csv"].decode("latin-1"))
# )
df_synth = pd.read_csv(
    "./20_intermediate_files/Synthetic_from_NB.csv", encoding="latin-1"
)
df_synth.head()

df_synth.info()

synth_tfidf = vec.transform(df_synth["tweets"].values.astype("U"))
predictions_synth = clf.predict(synth_tfidf)
print("Accuracy ={:.2%}".format(clf.score(synth_tfidf, df_synth["labels"])))

print(classification_report(df_synth["labels"], predictions_synth, digits=4))
