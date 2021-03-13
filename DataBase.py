import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# Настройки подключения
db_name = "rss_db"
db_password = "010112"
db_user_name = "postgres"
db_host_name = "127.0.0.1"
db_port_number ="5432"


connection = None
cursor = None

def open_db_connection():
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

def close_db_connection():
    global connection, cursor
    if  connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")


def create_database():
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

def create_tables():
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
        sql_create_tables = "CREATE TABLE public.rss_entries (raw_xml xml," \
                            "from_url VARCHAR(200),"\
                            "rss_author VARCHAR(100),"\
                            "rss_content text,"\
                            "rss_id VARCHAR(200),"\
                            "rss_published timestamp with time zone,"\
                            "rss_publisher VARCHAR(100),"\
                            "rss_tags VARCHAR(100),"\
                            "rss_title text,"\
                            "rss_updated timestamp with time zone,"\
                            "analized BOOLEAN DEFAULT FALSE,"\
                            "CONSTRAINT unq_ids UNIQUE (rss_id)"\
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


def drop_tables():
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


def write_one_row_in_db(xml_str, from_url_str, author_str,\
                    content_str, id_str, publisher_str, tags_str, title_str,\
                    published_str, updated_str):
    global connection, cursor
    rw = 0
    try:
        sql_insert_xml = "INSERT INTO public.rss_entries ("\
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
        sql_insert_xml = "INSERT INTO public.rss_entries ("\
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
        sql_select_10 = "SELECT rss_id, rss_title, rss_content, rss_published, from_url FROM rss_entries ORDER BY rss_published DESC"
        cursor.execute(sql_select_10)
        result = cursor.fetchall()
        #print(result)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        connection.rollback()

    return result


def RSS_feeds():
    opml_root = ET.parse("companies.opml.xml").getroot()
    rss_url = ""
    num = 0
    for tag in opml_root.findall('.//outline'):
        num += 1
        rss_url += f"{num}. {tag.items()[2][1]} \n"
    return rss_url
