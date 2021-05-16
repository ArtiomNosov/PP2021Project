
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import random, randint
from sklearn.feature_extraction.text import TfidfVectorizer
from psycopg2._psycopg import Error
from sklearn import model_selection, naive_bayes
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
import DataBase
import string
import nltk
from time import time
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

# минимальное значения кол-ва статей для начала анализа статей
minCountPapersForAnalysis = 50

regexp_token = RegexpTokenizer(r'\w+')

russian_stopwords = stopwords.words('english') + [a for a in string.punctuation]


def df_to_list_append(df):
    text_final = []
    for i in df:
        i = i[2:-2:1].split("', '")
        for j in i:
            text_final.append(j)
    return text_final


def PreparationForAnalize(df):
    df = df.drop(["rss_id", "id_censors"], axis=1)  # удаляем id

    df.rss_content.astype(str)  # печатаем данные

    df["tokenized_rss_text"] = df["rss_content"].fillna("").map(nltk.word_tokenize)

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


def Analysis(id_censor):

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

    if dfTrain.shape[0] < minCountPapersForAnalysis:
        print(f"Недостаточно оцененных пользователем статей для анализа!"
              f"Необходимый минимум: {minCountPapersForAnalysis}.\n На данный момент кол-во оцененных статей: " + str(dfTrain.shape[0]))
        return 0

    dfTrain = PreparationForAnalize(dfTrain)
    dfTrain = dfTrain.drop(["id_news"], axis=1)
    # Сделать отбор новостей за которые не голосовал отдельно взятый Вася и убрать LIMIT
    str_noname = ' SELECT news_entries.id_news,'\
                 'news_entries.rss_id,'\
				 ' NULL as id_censors,'\
                 'scores.score,'\
                 'news_entries.rss_content'\
                  ' FROM scores RIGHT JOIN news_entries ON scores.id_news = news_entries.id_news'\
				  ' WHERE scores.score is NULL LIMIT 40'
    dfPredict = pd.read_sql_query(str_noname, DataBase.connection)
    dfPredict = dfPredict.drop(["score"], axis=1)
    dfPredict = PreparationForAnalize(dfPredict)

    DataBase.close_db_connection()
    t1 = time()

    print(f" time= {t1 - t0:7.4f} seconds")

    # df.info()

    # df.isnull().sum() # печатает сумму

    # print(df.head(10))

    # Step 1
    lenTrain = dfTrain.size
    # dfTrain.append(dfPredict)

    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(dfTrain['text_final'], dfTrain['score'],
                                                                     test_size=0.3)

    # Step 2
    Encoder = LabelEncoder()
    Train_Y = Encoder.fit_transform(Train_Y)
    Test_Y = Encoder.fit_transform(Test_Y)

    # Step 3
    Tfidf_vect = TfidfVectorizer(max_features=50000)
    Tfidf_vect.fit(dfTrain['text_final'])
    Train_X_Tfidf = Tfidf_vect.transform(Train_X)
    Test_X_Tfidf = Tfidf_vect.transform(Test_X)
    print(Tfidf_vect.vocabulary_)
    # Step 4
    # fit the training dataset on the NB classifier
    Naive = naive_bayes.MultinomialNB()
    Naive.fit(Train_X_Tfidf, Train_Y)
    # predict the labels on validation dataset
    predictions_NB = Naive.predict(Test_X_Tfidf)
    # Use accuracy_score function to get the accuracy
    print("Naive Bayes Accuracy Score -> ", accuracy_score(predictions_NB, Test_Y) * 100)

    # Оцениваем статьи ML (удв опр условиям) и пишем в таблицу

    DataBase.open_db_connection()
    i = 0
    for iterator in dfPredict['id_news']:
        predict_grade = 0
        text_predict_iterator_X = (dfPredict.iloc[i][1]) #.drop(['id_news', 'rss_content', 'tokenized_rss_text'], axis = 1)
        Tfidf_vect_predict_iterator_X = Tfidf_vect.transform([text_predict_iterator_X])
        predict_grade = Naive.predict(Tfidf_vect_predict_iterator_X)
        # print(text_predict_iterator_X[0:1000:1])
        print(str(dfPredict.iloc[i][0]) + " - " + str(predict_grade[0]))
        try:
            sql_insert_xml = "INSERT INTO public.predict_scores (" \
                             "id_censors," \
                             "id_news," \
                             "predict_score" \
                             ") VALUES (%s,%s,%s);"
            DataBase.cursor.execute(sql_insert_xml, (id_censor, iterator, int(predict_grade[0])))
            DataBase.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
            DataBase.connection.rollback()
            try:
                sqlUpdate = 'UPDATE public.predict_scores SET predict_score = {!s} ' \
                            'WHERE id_censors = {!s} ' \
                            'AND id_news = {!s}'.format(predict_grade, id_censor, iterator)
                DataBase.cursor.execute(sqlUpdate)
                DataBase.connection.commit()
            except (Exception, Error) as error:
                DataBase.connection.rollback()
        i += 1
    DataBase.close_db_connection()
    return 0


Analysis(1)
