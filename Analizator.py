import time

# Импорты наших модулей

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import DataBase
import Analysis_Utils

# Константы
analysisFrequency = 20  # Раз в день 8640000000

# Timer

# Функция запускающая таймер
def analysis_grades():
    DataBase.open_db_connection()

    sql_request_str = 'SELECT id_censors, person_name, email, everyday_news FROM censors'

    DataBase.cursor.execute(sql_request_str)
    result = DataBase.cursor.fetchall()
    DataBase.close_db_connection()
    print(result)
    for iterator in result:
        print(iterator[0])
        Analysis_Utils.analysis(iterator[0])


while True:
    analysis_grades()
    time.sleep(analysisFrequency)
