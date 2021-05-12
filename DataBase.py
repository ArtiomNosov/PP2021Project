
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Настройки подключения
# TODO: сделать сохранение настроек в файле Properties.json или в переменных среды окружения windows
db_name = "article_predictor"
db_password = "010112"
db_user_name = "artiom"
db_host_name = "34.71.94.207"
db_port_number ="5432"

#Объект соединения с базой данных
connection = None
#Курсор в SQL – это область в памяти базы данных, которая предназначена для хранения последнего оператора SQL.
# Если текущий оператор – запрос к базе данных, в памяти сохраняется и строка данных запроса,
# называемая текущим значением, или текущей строкой курсора.
cursor = None

#Открывает соединение с базой данных
def open_db_connection():
    #Определяем глобальные для функции
    global connection, cursor
    try:
        # Подключение пользователя с правами к существующей базе данных
        connection = psycopg2.connect(user=db_user_name,\
                                      password=db_password,\
                                      host=db_host_name,\
                                      port=db_port_number,\
                                      database=db_name)
        #создаём область памяти для работы с БД
        cursor = connection.cursor()
        print("Открыто соединение с PostgreSQL")
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

def close_db_connection():
    global connection, cursor
    if  connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")

def get_user_id(username):
    global connection, cursor
    try:
        sql_select_10 = "SELECT id_censors " \
                        "FROM censors " \
                        "WHERE censors.person_name = %s::varchar"

        cursor.execute(sql_select_10, [username])
        result = cursor.fetchall()
        # print(result)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()

    return result[0][0]

def write_one_row_in_db(xml_str, from_url_str, author_str,\
                    content_str, id_str, publisher_str, tags_str, title_str,\
                    published_str, updated_str):
    global connection, cursor
    rw = 0
    try:
        sql_insert_xml = "INSERT INTO public.news_entries ("\
                            "raw_xml,"\
                            "from_url,"\
                            "rss_author,"\
                            "rss_content,"\
                            "rss_id,"\
                            "rss_publisher,"\
                            "rss_tags,"\
                            "rss_title,"\
                            "rss_published,"\
                            "rss_updated"\
                            ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        #print(xml_str)
        cursor.execute(sql_insert_xml, (xml_str, from_url_str, author_str,\
                    content_str, id_str,\
                    publisher_str, tags_str, title_str, published_str, updated_str))
        connection.commit()
        rw = 1
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()
    return rw


def write_list_in_db(list_rss):
    global connection, cursor
    rw = 0
    try:
        #формируем строку
        sql_insert_xml = "INSERT INTO public.news_entries ("\
                            "raw_xml,"\
                            "from_url,"\
                            "rss_author,"\
                            "rss_content,"\
                            "rss_id,"\
                            "rss_publisher,"\
                            "rss_tags,"\
                            "rss_title,"\
                            "rss_published,"\
                            "rss_updated"\
                            ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        #print(xml_str)
        cursor.executemany(sql_insert_xml, list_rss)
        connection.commit()
        # В rw пишем сколько реально строк мы записали
        rw = cursor.rowcount
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()
        # Если скопом не получилось - Вставляем по 1
        for en in list_rss:
            if write_one_row_in_db(en[0], en[1], en[2], en[3], en[4], en[5], en[6], en[7], en[8], en[9]) > 0:
                rw += 1
    print(f"Вставлено {rw:d} строк")
    return rw

def get_all_rss():
    global connection, cursor
    try:
        sql_select_10 = "SELECT rss_id, rss_title, rss_content, rss_published, from_url FROM public.news_entries ORDER BY rss_published DESC"
        cursor.execute(sql_select_10)
        result = cursor.fetchall()
        #print(result)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()

    return result

def get_all_analized_rss(person_id):
    global connection, cursor
    try:
        sql_select_10 = "SELECT rss_id, rss_title, rss_content, rss_published, from_url, predict_score " \
                        "FROM news_entries JOIN predict_scores ON news_entries.id_news = predict_scores.id_news " \
                        "WHERE predict_scores.id_censors = {!s} ORDER BY predict_score DESC".format(person_id)


        cursor.execute(sql_select_10)
        result = cursor.fetchall()
        # print(result)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()

    return result

# Функция добавляющая одного пользователя в базу данных
def insert_one_person(person_name):
    resuilt = 0
    try:

        sql_insert_one_person = "INSERT INTO public.censors ("\
                            "person_name"\
                            ") VALUES (%s);"
        #
        cursor.execute(sql_insert_one_person, (person_name,))
        connection.commit()
        resuilt = 1
    except (Exception, Error) as error:
        #print("Пользователь {!s} не добавлен".format(person_name))
        #print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()

    return resuilt

def write_one_row_in_censors(person_name, rss_id, grade):
    global connection, cursor
    internal_id_censor = 0
    internal_id_news = 0
    # TODO: Нужно переделать - тупо пробуем добавить пользователя, если он уже есть то не добавится, если нет
    # - точно будет!
    insert_one_person(person_name)
    # Получим id пользователя
    try:
        sql_get_person_name = "SELECT id_censors FROM censors WHERE person_name = '{!s}';".format(person_name)
        cursor.execute(sql_get_person_name)
        result = cursor.fetchall()
        internal_id_censor = result[0]
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    # Получим id новости по rss_id
    try:
        sql_get_news_id = "SELECT id_news FROM news_entries WHERE rss_id = '{!s}';".format(rss_id)
        cursor.execute(sql_get_news_id)
        result = cursor.fetchall()
        internal_id_news = result[0]
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    #
    try:
        #INSERT INTO scores(score, id_censors, id_news) VALUES (5, (SELECT id_censors FROM censors WHERE person_name = 'John Hodk'), (SELECT id_news FROM news_entries WHERE
        #rss_id = '123'));
        sql_insert_xml = "INSERT INTO public.scores ("\
                            "id_censors,"\
                            "id_news,"\
                            "score"\
                            ") VALUES (%s,%s,%s);"
        cursor.execute(sql_insert_xml, (internal_id_censor, internal_id_news, grade))
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()
