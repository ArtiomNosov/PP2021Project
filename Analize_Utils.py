from sklearn import model_selection, naive_bayes
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

import DataBase

import string

import nltk
from time import time
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

regexp_token = RegexpTokenizer(r'\w+')

russian_stopwords = stopwords.words('english') + [a for a in string.punctuation]


from sklearn.feature_extraction.text import TfidfVectorizer

import pandas as pd
def Analize(id_censor):

    t0 = time()
    DataBase.open_db_connection()
    str_noname = 'SELECT news_entries.id_news,'\
    'news_entries.rss_id,'\
    'censors.id_censors,'\
    'scores.score,'\
    'news_entries.rss_content'\
    ' FROM news_entries JOIN scores ON scores.id_news = news_entries.id_news'\
    ' JOIN censors ON scores.id_censors = censors.id_censors WHERE censors.id_censors = {!s}'.format(id_censor)
    print(str_noname)
    df = pd.read_sql_query(str_noname, DataBase.connection)
    DataBase.close_db_connection()
    t1 = time()

    print(f" time= {t1 - t0:7.4f} seconds")
    if df.size < 1:
        return
    # df.info()

    df.isnull().sum() # печатает сумму

    df = df.drop(["id_news", "rss_id", "id_censors"], axis=1) # удаляем id

    df.rss_content.astype(str) # печатаем данные
    # print(df.head(10))

    df["tokenized_rss_text"] = df["rss_content"].fillna("").map(nltk.word_tokenize)
    # print(df.head(10))

    tag_map = nltk.defaultdict(lambda: wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    for index, entry in enumerate(df["tokenized_rss_text"]):
        # Declaring Empty List to store the words that follow the rules for this step
        Final_words = []
        # Initializing WordNetLemmatizer()
        word_Lemmatized = WordNetLemmatizer()
        # pos_tag function below will provide the 'tag' i.e if the word is Noun(N) or Verb(V) or something else.
        for word, tag in nltk.pos_tag(entry):
            # Below condition is to check for Stop words and consider only alphabets
            if word not in stopwords.words('english') and word.isalpha():
                word_Final = word_Lemmatized.lemmatize(word, tag_map[tag[0]])
                Final_words.append(word_Final)
        # The final processed set of words for each iteration will be stored in 'text_final'
        df.loc[index, 'text_final'] = str(Final_words)
        # Далее везде заменяем rss_text на text_final

    # print(df.head(10))

    # Step 1
    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(df['text_final'], df['score'],
                                                                        test_size=0.6)
    # Step 2
    Encoder = LabelEncoder()
    Train_Y = Encoder.fit_transform(Train_Y)
    Test_Y = Encoder.fit_transform(Test_Y)

    # Step 3
        Tfidf_vect = TfidfVectorizer(max_features=5000)
    Tfidf_vect.fit(df['text_final'])
    Train_X_Tfidf = Tfidf_vect.transform(Train_X)
    Test_X_Tfidf = Tfidf_vect.transform(Test_X)

    # Step 4
    # fit the training dataset on the NB classifier
    Naive = naive_bayes.MultinomialNB()
    Naive.fit(Train_X_Tfidf, Train_Y)
    # predict the labels on validation dataset
    predictions_NB = Naive.predict(Test_X_Tfidf)
    # Use accuracy_score function to get the accuracy
    print("Naive Bayes Accuracy Score -> ", accuracy_score(predictions_NB, Test_Y) * 100)
    print(predictions_NB)
    # Оцениваем статьи ML (удв опр условиям) и пишем в таблицу