import threading

# Константы
analysisFrequency = 15 # Раз в день 8640000000
counter = 0

# Функция запускающая таймер
def analize_grades():
    global counter
    # timer = threading.Timer(interval, function,
    #                            args=None, kwargs=None)
    # Параметры:
    # interval - интервал запуска вызываемого объекта (функции),
    # function - вызываемый объект (функция),
    # args=None - позиционные аргументы function,
    # kwargs=None - ключевые аргументы function.
    counter = counter + 1
    print(counter)

#timer = threading.Timer(analysisFrequency, analize_gradesv)
analize_grades()
