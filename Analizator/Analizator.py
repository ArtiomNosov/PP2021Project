import time

# Импорты наших модулей
import DataBase
import Analize_Utils

# Константы
analysisFrequency = 5  # Раз в день 8640000000

# Timer


# Функция запускающая таймер
def analize_grades():
    DataBase.open_db_connection()

    sql_request_str = 'SELECT id_censors, person_name, email, everyday_news FROM censors'

    DataBase.cursor.execute(sql_request_str)
    result = DataBase.cursor.fetchall()
    DataBase.close_db_connection()

    for eterator in result:
        print(eterator[0])
        Analize_Utils.analysis(eterator[0])


while(True):
   time.sleep(analysisFrequency)
   analize_grades()
