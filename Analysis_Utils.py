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

def function_return_random_grade(str):
    print(str)
    return randint(1, 5)

def preparation_for_analysis(data_frame):
    data_frame = data_frame.drop(["id_news", "rss_id", "id_censors"], axis=1)  # удаляем id

    data_frame.rss_content.astype(str)  # печатаем данные
    # print(df.head(10))

    data_frame["tokenized_rss_text"] = data_frame["rss_content"].fillna("").map(nltk.word_tokenize)
    # print(df.head(10))

    tag_map = nltk.defaultdict(lambda: wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    for index, entry in enumerate(data_frame["tokenized_rss_text"]):
        # Declaring Empty List to store the words that follow the rules for this step
        final_words = []
        # Initializing WordNetLemmatizer()
        word_Lemmatized = WordNetLemmatizer()
        # pos_tag function below will provide the 'tag' i.e if the word is Noun(N) or Verb(V) or something else.
        for word, tag in nltk.pos_tag(entry):
            # Below condition is to check for Stop words and consider only alphabets
            if word not in stopwords.words('english') and word.isalpha():
                word_final = word_Lemmatized.lemmatize(word, tag_map[tag[0]])
                final_words.append(word_final)
        # The final processed set of words for each iteration will be stored in 'text_final'
        data_frame.loc[index, 'text_final'] = str(final_words)
        # Далее везде заменяем rss_text на text_final
    return data_frame

def analysis(id_censor):
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
    df_train = pd.read_sql_query(str_noname, DataBase.connection)

    df_train = preparation_for_analysis(df_train)

    # Сделать отбор новостей за которые не голосовал отдельно взятый Вася и убрать LIMIT
    str_noname = ' SELECT news_entries.id_news,'\
                 'news_entries.rss_id,'\
				 ' NULL as id_censors,'\
                 'scores.score,'\
                 'news_entries.rss_content'\
                  ' FROM scores RIGHT JOIN news_entries ON scores.id_news = news_entries.id_news'\
				  ' WHERE scores.score is NULL LIMIT 40'
    df_predict = pd.read_sql_query(str_noname, DataBase.connection)

    df_predict = preparation_for_analysis(df_predict)

    DataBase.close_db_connection()
    t1 = time()

    print(f" time= {t1 - t0:7.4f} seconds")

    # df.info()

    # df.isnull().sum() # печатает сумму

    # print(df.head(10))

    # Step 1
    lenTrain = df_train.size
    #dfTrain.append(dfPredict)

    # Перемешиване набора для обучения и тренировки
    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(df_train['text_final'], df_train['score'],
                                                                     test_size=0.3)

    # Step 2
    # Делаем из набора слов набор категорий
    Encoder = LabelEncoder()
    Train_Y = Encoder.fit_transform(Train_Y)
    Test_Y = Encoder.fit_transform(Test_Y)
    print(Train_Y)
    print(Test_Y)

    # Step 3
    Tfidf_vect = TfidfVectorizer(max_features=5000)
    Tfidf_vect.fit(df_train['text_final'])
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
    # TODO: Отладить в цикле for неправильное поведение
    DataBase.open_db_connection()
    for iterator in df_predict['id_news']:
        predict_grade = function_return_random_grade(iterator)
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

# Функция сохранения объекта naive_bayes.MultinomialNB() обученного
# для определённого пользователя по пути Sourse/Saved_ML_forEveryone
# В функцию передаём id объекта и путь сохранения и имя файла для сохранения
# TODO: Подумать, что будет, если поверх старого фала сохранить новый с таким же названием
# TODO: Если будем сохранять объекты обученные для анализа методом Баеса, то необходимо внедрить общий словарь id
# def saveObject(object_name, path_to_directory, file_name):
#     pickle.dump(object_name, open(os.path.join(str(path_to_directory) ,"ML_" + str(file_name) + ".sav"), "w+")
#     return 0

# Функция для возвращения объекта из файла обратно в программу
# Аргументы: имя необходимого файла, путь до этого файла.
#def unpaсkObject(path_to_directory, file_name):