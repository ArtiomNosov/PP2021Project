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
        connection = psycopg2.connect(user=DataBase.db_user_name,
                                      password=DataBase.db_password,
                                      host=DataBase.db_host_name,
                                      port=DataBase.db_port_number,
                                      database=DataBase.db_name)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        # SQL запрос для создания таблицы
        sql_create_tables = "CREATE TABLE public.news_entries (" \
                            "ID serial primary key," \
                            "raw_xml xml," \
                            "from_url VARCHAR(200)," \
                            "rss_author VARCHAR(100)," \
                            "rss_content text," \
                            "rss_id VARCHAR(200)," \
                            "rss_published timestamp with time zone," \
                            "rss_publisher VARCHAR(100)," \
                            "rss_tags VARCHAR(100)," \
                            "rss_title text," \
                            "rss_updated timestamp with time zone," \
                            "analized BOOLEAN DEFAULT FALSE," \
                            "CONSTRAINT unq_ids UNIQUE (rss_id)" \
                            ");"  # Задаём ограничение на CONSTRATE на требование уникальности rss_id

        # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
        sql_alter_tableds = "ALTER TABLE public.rss_entries OWNER to {!s};".format(DataBase.db_user_name)

        # Выполняем sql запросы на создание таблицы
        cursor.execute(sql_create_tables)
        # Выполняем sql запрос на изменение таблицы на изменение пользователя
        cursor.execute(sql_alter_tableds)

        #Создаём таблицу пользователей
        sql_create_tables = "CREATE TABLE public.censors (" \
                            "ID serial primary key," \
                            "person_name VARCHAR(20)," \
                            "email VARCHAR(100)" \
                            "everydayNews BOOLEAN DEFAULT FALSE" \
                            ");"

        # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
        sql_alter_tableds = "ALTER TABLE public.censors OWNER to {!s};".format(DataBase.db_user_name)

        # Выполняем sql запросы на создание таблицы
        cursor.execute(sql_create_tables)
        # Выполняем sql запрос на изменение таблицы на изменение пользователя
        cursor.execute(sql_alter_tableds)

        # Создаём таблицу оценки
        sql_create_tables = "CREATE TABLE public.scores (" \
                            "FOREIGN KEY (ID_censors) REFERENCES censors (ID)" \
                            "FOREIGN KEY (ID_news_entries) REFERENCES news_entries (ID)," \
                            "score NUMERIC," \
                            ");"

        # sql запрос для привязки к другому пользователю по умолчанию таблица привязана непонятно к кому
        sql_alter_tableds = "ALTER TABLE public.censors OWNER to {!s};".format(DataBase.db_user_name)

        # Выполняем sql запросы на создание таблицы
        cursor.execute(sql_create_tables)
        # Выполняем sql запрос на изменение таблицы на изменение пользователя
        cursor.execute(sql_alter_tableds)


        # коммитим
        connection.commit()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
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
        sql_drop_tables = 'drop table rss_entries;'
        cursor.execute(sql_drop_tables)
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")