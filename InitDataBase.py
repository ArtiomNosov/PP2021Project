######################################################################################
# InitDataBase.py - В данном модуле набор функций для создания пустой базы дынных
# (стартовое решение)
# Author Artiom Nosov <artiom-nj@mail.ru>
# version: 0.0.01
######################################################################################

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import DataBase

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


#создание базы данных
def create_database():
    #Описываем функции от трая до екзепта и у нас есть блок кода
    try:
        # Подключение пользователя с правами к существующей базе данных
        connection = psycopg2.connect(user=DataBase.db_user_name,
                                      password=DataBase.db_password,
                                      host=DataBase.db_host_name,
                                      port=DataBase.db_port_number)
        # Коммиты будут происходить автоматически
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        #Записываем будующую переменную строковую
        sql_create_database = "CREATE DATABASE {!s} WITH OWNER = {!s}"\
                              " ENCODING = 'UTF8' CONNECTION LIMIT = -1".format(DataBase.db_name, DataBase.db_user_name)
        #print(sql_create_database)
        cursor.execute(sql_create_database)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    #finally выполнится в любом случае
    finally:
        #Если соединение было установлено
        if connection:
            #Закрываем курсор
            cursor.close()
            #Закрываем соединение
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def create_tables():
    try:
        # Подключение к существующей базе данных
        DataBase.connection = psycopg2.connect(user=DataBase.db_user_name,
                                      password=DataBase.db_password,
                                      host=DataBase.db_host_name,
                                      port=DataBase.db_port_number,
                                      database=DataBase.db_name)
        # Курсор для выполнения операций с базой данных
        DataBase.cursor = DataBase.connection.cursor()
        # SQL запрос для создания таблицы
        sql_create_tables = "CREATE TABLE public.news_entries (" \
                            "id_news serial primary key," \
                            "raw_xml xml," \
                            "from_url VARCHAR(200)," \
                            "rss_author VARCHAR(100)," \
                            "rss_content text," \
                            "rss_id VARCHAR(200)," \
                            "rss_published timestamp with time zone," \
                            "rss_publisher VARCHAR(200)," \
                            "rss_tags VARCHAR(200)," \
                            "rss_title text," \
                            "rss_updated timestamp with time zone," \
                            "analized BOOLEAN DEFAULT FALSE," \
                            "CONSTRAINT unq_ids UNIQUE (rss_id)" \
                            ");"  # Задаём ограничение на CONSTRATE на требование уникальности rss_id

        # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
        sql_alter_tableds = "ALTER TABLE public.news_entries OWNER to {!s};".format(DataBase.db_user_name)

        # Выполняем sql запросы на создание таблицы
        DataBase.cursor.execute(sql_create_tables)
        # Выполняем sql запрос на изменение таблицы на изменение пользователя
        DataBase.cursor.execute(sql_alter_tableds)

        #Создаём таблицу пользователей
        sql_create_tables = "CREATE TABLE public.censors (" \
                            "ID_censors serial primary key," \
                            "person_name VARCHAR(20)," \
                            "email VARCHAR(100)," \
                            "everyday_news BOOLEAN DEFAULT FALSE," \
                            "CONSTRAINT unq_person_name UNIQUE (person_name)" \
                            ");"

        # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
        sql_alter_tableds = "ALTER TABLE public.censors OWNER to {!s};".format(DataBase.db_user_name)

        # Выполняем sql запросы на создание таблицы
        DataBase.cursor.execute(sql_create_tables)
        DataBase.connection.commit()
        # Выполняем sql запрос на изменение таблицы на изменение пользователя
        DataBase.cursor.execute(sql_alter_tableds)
        DataBase.connection.commit()


        # Создаём таблицу оценки
        sql_create_tables = "CREATE TABLE public.scores ("\
                            "id_censors integer REFERENCES public.censors (id_censors) ON DELETE CASCADE," \
                            "id_news integer REFERENCES public.news_entries (id_news) ON DELETE CASCADE," \
                            "score NUMERIC," \
							"PRIMARY KEY (id_censors, id_news)" \
                            ");"

        # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
        sql_alter_tableds = "ALTER TABLE public.scores OWNER to {!s};".format(DataBase.db_user_name)

        # Выполняем sql запросы на создание таблицы
        DataBase.cursor.execute(sql_create_tables)
        # Выполняем sql запрос на изменение таблицы на изменение пользователя
        DataBase.cursor.execute(sql_alter_tableds)

        # Создаём таблицу предсказанных моделью оценок
        sql_create_tables = "CREATE TABLE public.predict_scores (" \
                            "id_censors integer REFERENCES public.censors (id_censors) ON DELETE CASCADE," \
                            "id_news integer REFERENCES public.news_entries (id_news) ON DELETE CASCADE," \
                            "predict_score NUMERIC," \
                            "PRIMARY KEY (id_censors, id_news)" \
                            ");"

        # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
        sql_alter_tableds = "ALTER TABLE public.predict_scores OWNER to {!s};".format(DataBase.db_user_name)

        # Выполняем sql запросы на создание таблицы
        DataBase.cursor.execute(sql_create_tables)
        # Выполняем sql запрос на изменение таблицы на изменение пользователя
        DataBase.cursor.execute(sql_alter_tableds)



        # коммитим
        DataBase.connection.commit()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if DataBase.connection:
            DataBase.cursor.close()
            DataBase.connection.close()
            print("Соединение с PostgreSQL закрыто")

def drop_tables():
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user=DataBase.db_user_name,
                                      password=DataBase.db_password,
                                      database=DataBase.db_name,
                                      host=DataBase.db_host_name,
                                      port=DataBase.db_port_number)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()

        # Удаляем scores
        sql_drop_tables = 'drop table scores;'
        cursor.execute(sql_drop_tables)
        connection.commit()

        #Удаляем таблицу news_entries
        sql_drop_tables = 'drop table news_entries;'
        cursor.execute(sql_drop_tables)
        connection.commit()

        #Удаляем censors
        sql_drop_tables = 'drop table censors;'
        cursor.execute(sql_drop_tables)
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


# drop_tables()
# create_tables()

# # Подключение к существующей базе данных
# DataBase.connection = psycopg2.connect(user=DataBase.db_user_name,
#                                        password=DataBase.db_password,
#                                        host=DataBase.db_host_name,
#                                        port=DataBase.db_port_number,
#                                        database=DataBase.db_name)
# # Курсор для выполнения операций с базой данных
# DataBase.cursor = DataBase.connection.cursor()
#
# # Создаём таблицу оценки
# sql_create_tables = "CREATE TABLE public.scores ("\
#                     "id_censors integer REFERENCES public.censors (id_censors)," \
#                     "id_news integer REFERENCES public.news_entries (id_news)," \
#                     "score NUMERIC," \
#                     "PRIMARY KEY (id_censors, id_news)" \
#                     ");"
#
# # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
# sql_alter_tableds = "ALTER TABLE public.scores OWNER to {!s};".format(DataBase.db_user_name)
#
# # Выполняем sql запросы на создание таблицы
# DataBase.cursor.execute(sql_create_tables)
# # Выполняем sql запрос на изменение таблицы на изменение пользователя
# DataBase.cursor.execute(sql_alter_tableds)
#
# # коммитим
# DataBase.connection.commit()
#
# DataBase.connection.close()