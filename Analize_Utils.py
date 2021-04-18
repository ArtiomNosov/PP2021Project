from random import random, randint

from psycopg2._psycopg import Error
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

def FunctionReturnRandomGrade(arg, str):
    print(str)
    return randint(1, 5)

def PreparationForAnalize(df):
    df = df.drop(["id_news", "rss_id", "id_censors"], axis=1)  # удаляем id

    df.rss_content.astype(str)  # печатаем данные
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
    return df

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
    dfTrain = pd.read_sql_query(str_noname, DataBase.connection)

    dfTrain = PreparationForAnalize(dfTrain)

    # Сделать отбор новостей за которые не голосовал отдельно взятый Вася и убрать LIMIT
    str_noname = ' SELECT news_entries.id_news,'\
                 'news_entries.rss_id,'\
				 ' NULL as id_censors,'\
                 'scores.score,'\
                 'news_entries.rss_content'\
                  ' FROM scores RIGHT JOIN news_entries ON scores.id_news = news_entries.id_news'\
				  ' WHERE scores.score is NULL LIMIT 40'
    dfPredict = pd.read_sql_query(str_noname, DataBase.connection)

    # dfPredict = PreparationForAnalize(dfPredict)

    DataBase.close_db_connection()
    t1 = time()

    print(f" time= {t1 - t0:7.4f} seconds")

    #Подумать над условиями выхода
    if dfTrain.size < 1:
        return
    if dfPredict.size < 1:
        return

    # df.info()

    # df.isnull().sum() # печатает сумму

    # print(df.head(10))

    # Step 1
    lenTrain = dfTrain.size
    #dfTrain.append(dfPredict)

    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(dfTrain['text_final'], dfTrain['score'],
                                                                     test_size=0.3)

    # Step 2
    Encoder = LabelEncoder()
    Train_Y = Encoder.fit_transform(Train_Y)
    Test_Y = Encoder.fit_transform(Test_Y)

    # Step 3
    Tfidf_vect = TfidfVectorizer(max_features=5000)
    Tfidf_vect.fit(dfTrain['text_final'])
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

    # Оцениваем статьи ML (удв опр условиям) и пишем в таблицу
    # функция заглушка FunctionThanReturnGrade(статья) -> [1 ,2, 3, 4, 5]
    arg = 1
    DataBase.open_db_connection()
    for iterator in dfPredict['id_news']:
        predict_grade = FunctionReturnRandomGrade(arg, iterator)
        try:
            # INSERT INTO scores(score, id_censors, id_news) VALUES (5, (SELECT id_censors FROM censors WHERE person_name = 'John Hodk'), (SELECT id_news FROM news_entries WHERE
            # rss_id = '123'));
            sql_insert_xml = "INSERT INTO public.predict_scores (" \
                             "id_censors," \
                             "id_news," \
                             "predict_score" \
                             ") VALUES (%s,%s,%s);"
            DataBase.cursor.execute(sql_insert_xml, (id_censor, iterator, predict_grade))
            DataBase.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
            DataBase.connection.rollback()
            try:
                sqlUpdate = 'UPDATE public.predict_scores SET predict_score = {!s} WHERE id_censors = {!s} AND id_news = {!s}'.format(predict_grade, id_censor, iterator)
                DataBase.cursor.execute(sqlUpdate)
                DataBase.connection.commit()
            except (Exception, Error) as error:
                DataBase.connection.rollback()
    DataBase.close_db_connection()