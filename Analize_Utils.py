
import DataBase

import string
#from __future__ import print_function

from time import time
from nltk import word_tokenize, Text
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer, WordNetLemmatizer

regexp_token = RegexpTokenizer(r'\w+')

russian_stopwords = stopwords.words('english') + [a for a in string.punctuation]


from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer

import pandas as pd

t0 = time()
DataBase.open_db_connection()
df = pd.read_sql_query('SELECT * FROM rss_entries', DataBase.connection)
t1 = time()

print(f" time= {t1-t0:7.4f} seconds")
rss_text = ""
rss_text = df['rss_content'].values[1]
rss_text = rss_text.lower()

all_tokens = regexp_token.tokenize(rss_text)
print(len(all_tokens))
clear_tokens = [single_token for single_token in all_tokens if single_token not in russian_stopwords]
clear_tokens = list(set(clear_tokens))
print(f" After clearance:{len(clear_tokens)}")


lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

buf = []
for single_token in clear_tokens:
    buf.append(stemmer.stem(single_token))
clear_tokens = buf
clear_tokens = list(set(clear_tokens))
print(f" After stem:{len(clear_tokens)}")

buf = []
for single_token in clear_tokens:
    buf.append(lemmatizer.lemmatize(single_token, wordnet.VERB))
clear_tokens = buf
clear_tokens = list(set(clear_tokens))
print(f" After lemmanizer:{len(clear_tokens)}")

count_vectorizer = CountVectorizer()
features = count_vectorizer.fit_transform(clear_tokens).toarray()
print(features)