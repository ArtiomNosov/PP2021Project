import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Настройки подключения
db_name = "person_list"
db_password = "F9285858ND"
db_user_name = "postgres"
db_host_name = "127.0.0.1"
db_port_number ="5432"

connection = None
cursor = None


def open_db_connection_p():
    global connection, cursor
    try:
        connection = psycopg2.connect(user=db_user_name,\
                                      password=db_password,\
                                      host=db_host_name,\
                                      port=db_port_number,\
                                      database=db_name)
        cursor = connection.cursor()
        print("Открыто соединение с PostgreSQL")
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


def close_db_connection_p():
    global connection, cursor
    if  connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")


def create_database_p():
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user=db_user_name,
                                      password=db_password,
                                      host=db_host_name,
                                      port=db_port_number)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        sql_create_database = "CREATE DATABASE {!s} WITH OWNER = {!s}  ENCODING = 'UTF8' CONNECTION LIMIT = -1".format(db_name, db_user_name)
        print(sql_create_database)
        cursor.execute(sql_create_database)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def create_tables_p():
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user=db_user_name,
                                      password=db_password,
                                      host=db_host_name,
                                      port=db_port_number,
                                      database=db_name)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        # SQL для создания таблицы
        sql_create_tables = "CREATE TABLE public.rss_entries (" \
                            "ID serial primary key,"\
                            "person_name VARCHAR(20),"\
                            "rss_id VARCHAR(1000),"\
                            "grade VARCHAR(200)"\
                            ");"
        sql_alter_tableds = "ALTER TABLE public.rss_entries OWNER to postgres;"

        cursor.execute(sql_create_tables)
        cursor.execute(sql_alter_tableds)
        connection.commit()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def drop_tables_p():
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user=db_user_name,
                                      password=db_password,
                                      database=db_name,
                                      host=db_host_name,
                                      port=db_port_number)
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


def write_one_row_in_db_p(person_name, rss_id, grade):
    global connection, cursor
    try:
        sql_insert_xml = "INSERT INTO public.rss_entries ("\
                            "person_name,"\
                            "rss_id,"\
                            "grade"\
                            ") VALUES (%s,%s,%s);"
        cursor.execute(sql_insert_xml, (person_name, rss_id, grade))
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()
