#UPDATE 0.04.1
#Добавлена команда /help, выводящая все существующие в боте команды

#Импорты сторонних модулей
import ssl
import telebot
from telebot import types
from psycopg2 import Error
import time

#Импорт наших модулей
import DataBase
import RSS_Utils #Добавляем наши утилиты связанные с RSS
import Mail_Utils #Добавляем наши утилиты для парсинга и сбора почты
import Analize_Utils #Добавляем наши утилиты анализа данных

# TODO: Убрать токен из текста программы
bot = telebot.TeleBot('1631242798:AAEBKc1x16vZpEO3QkzAecK5HEM8jE2v510') # Токен telegram его бы лучше здесь не хранить.
person_name = "No_Name"     # Имя гостя (по умолчанию No_Name)
page_count = 5              # Кол-во статей за 1 вывод
page = 0                    # Текущая страница
everydayNews = False        # Ежедневная рассылка новостей
timeOnOnePost = 60          # Через какое время будут присылаться новости (в секундах)

# Создание списка новостей
def get_news():
    rss_list = []
    DataBase.open_db_connection()
    list_rss_news = DataBase.get_all_rss()
    DataBase.close_db_connection()
    for row in list_rss_news:
        print(row)
        content = "" + row[2]
        rss_list.append([f"   <b><u>{row[1]}</u></b>\n <b>Опубликовано:</b> {row[3]:%d/%m/%Y}\n <b>Сайт: {row[0]}</b>\n======================================\n{content[0:500]}", row[0]])
    return rss_list


# Исправление ошибки с сертификатом ssl костыль просто отменяем проверку
ssl._create_default_https_context = ssl._create_unverified_context


#Регистрация оценкок пользователя
def register_grades(person_name, rss_list, grade, number_of_artical, page):
    global page_count
    DataBase.open_db_connection()
    DataBase.write_one_row_in_censors(person_name, rss_list[int(number_of_artical)][1], int(grade))
    print("Article number " + str(int(number_of_artical) + 1) + " written.")
    DataBase.close_db_connection()


#Получение статей
rss_list = get_news()


#TODO: допилить приветствие, сделать в нем регистрацию пользователя
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Приветсвтуем вас в ....(ну надо же что-нибудь написать)', None)


#Команда, выводящая все существующие в боте команды (кроме /start)
@bot.message_handler(commands=['help'])
def start_message(message):
    global page_count
    bot.send_message(message.chat.id, f'<b>Этот бот имеет следующие команды:</b>\n'\
                                      f'/list - вывод всех ваших RSS ссылок, на которые вы в данный момент подписаны,\n'\
                                      f'/register - регистрация пользователя, т.е. бот запоминает ваше имя (необходимо для бд),\n'\
                                      f'/newnews - выводится последние {page_count} новостей,\n'\
                                      f'/everydayNews - включение/выключение еедневных новостей (пока что отключена).', parse_mode="HTML")


#Выводим лист всех RSS подписок.
#TODO: сделать возможность удалять или дополнять этот лист RSS подписками по вводу 1й RSS ссылки
@bot.message_handler(commands=['list'])
def start_message(message):
    bot.send_message(message.chat.id, RSS_Utils.RSS_feeds(), None)


# Регистрация пользователя по имени, т.е. запись его в глобальную переменную
#TODO: фигня какая-то. Вообще переделать и сделать автоматическим.
@bot.message_handler(commands=['register'])
def start_message(message):
    global person_name
    person_name = message.from_user.id
    DataBase.open_db_connection()
    DataBase.insert_one_person(person_name)
    DataBase.close_db_connection()
    bot.send_message(message.chat.id, "Регистрация пользователя завершена!", None)


#Вывод следующих page_count статей
@bot.message_handler(commands=['newnews'])
def next_news(message):
    global rss_list
    global page
    global page_count
    global number_of_artical
    if (page + 1)*page_count < len(rss_list):
        for i in range(page_count*page, page_count*(page + 1)):
            keyboard = types.InlineKeyboardMarkup()
            one_k = types.InlineKeyboardButton(text='1', callback_data='1'+str(i))
            two_k = types.InlineKeyboardButton(text='2', callback_data='2'+str(i))
            three_k = types.InlineKeyboardButton(text='3', callback_data='3'+str(i))
            four_k = types.InlineKeyboardButton(text='4', callback_data='4'+str(i))
            five_k = types.InlineKeyboardButton(text='5', callback_data='5'+str(i))
            keyboard.add(one_k, two_k, three_k)
            keyboard.add(four_k, five_k)
            try:
                bot.send_message(message.chat.id, rss_list[i][0], reply_markup=keyboard, parse_mode="HTML")
            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL", error)
            time.sleep(1)
    else:
        for i in range(page_count*page, len(rss_list)):
            keyboard = types.InlineKeyboardMarkup()
            one_k = types.InlineKeyboardButton(text='1', callback_data='1'+str(i))
            two_k = types.InlineKeyboardButton(text='2', callback_data='2'+str(i))
            three_k = types.InlineKeyboardButton(text='3', callback_data='3'+str(i))
            four_k = types.InlineKeyboardButton(text='4', callback_data='4'+str(i))
            five_k = types.InlineKeyboardButton(text='5', callback_data='5'+str(i))
            keyboard.add(one_k, two_k, three_k)
            keyboard.add(four_k, five_k)
            try:
                bot.send_message(message.chat.id, rss_list[i][0], reply_markup=keyboard, parse_mode="HTML")
            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL", error)
    page += 1


@bot.message_handler(commands=['everydayNews'])
def everydayNews_YN(message):
    keyboardYN = types.InlineKeyboardMarkup()
    one_k = types.InlineKeyboardButton(text='Да', callback_data='yes_everydayNews')
    two_k = types.InlineKeyboardButton(text='Нет', callback_data='no_everydayNews')
    keyboardYN.add(one_k, two_k)
    bot.send_message(message.chat.id, "Вы хотите каждый день получать рассылку новостей?", reply_markup=keyboardYN)



#Получаем ответ пользователя, т.е. обработка всех ответов кнопочек и всего подобного
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global rss_list
    global page;
    if call.data[0] in ("1", "2", "3", "4", "5"):
        register_grades(person_name, rss_list, call.data[0], call.data[1], page)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Ваша оценка статьи записана!")
    global everydayNews




    if call.data == "yes_everydayNews":
        everydayNews = True
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Теперь каждый день в это время вам будут приходить новые статьи!')
    if call.data == "no_everydayNews":
        everydayNews = False
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Ежедневные новости отключены!')


bot.polling(none_stop=True, interval=1)
