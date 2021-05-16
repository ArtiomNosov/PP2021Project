#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ssl
import telebot
from telebot import types
from psycopg2 import Error
import datetime as dt
import time


# Импорт наших модулей
import DataBase
import RSS_Utils #Добавляем наши утилиты связанные с RSS
# import Mail_Utils #Добавляем наши утилиты для парсинга и сбора почты
# import Analize_Utils #Добавляем наши утилиты анализа данных
DataBase.open_db_connection()
# TODO: Защита от спама. Когда много раз прописывется команда newnews, то бот ложится.
# TODO: Cделать автоматическую регистрацию пользователя.
#  Сейчас при начале диалога автоматически прописывается
#  команда start и пользователь регистрируется, если пользователь
#  не зарегистрирован и пробует попросить новости, то всё слетает.
# TODO: Сделать индивидуальный лист рекомендаций для каждого пользователя.
#  Сейчас для всех пользователей один список рекомендаций.
# Считывает токен из файла
with open("token.txt", "r") as f:
    text = f.readline()
    print("Token your bot is")
    print(text)


bot = telebot.TeleBot(text.rstrip())  # Токен telegram его бы лучше здесь не хранить.
person_name = "No_Name"      # Имя гостя (по умолчанию No_Name)
page_count = 5               # Кол-во статей за 1 вывод
everydayNews = False         # Ежедневная рассылка статей
timeOnOnePost = 60           # Через какое время будут присылаться статьи (в секундах)
days_limit = 150             # Насколько старые статьи будут присылаться пользователям (в днях)
user_pages = {}              # Словарь со страницами пользователей


# Функция сравнения даты статьи с текущей датой. Выдает True <=> текущая дата - days_limit <= дата статьи
def row_days_analize(row_3):
    limitedday = dt.datetime.today() - dt.timedelta(days=days_limit)
    paperday = dt.datetime.strptime(f"{row_3[3]:%d-%m-%Y}", "%d-%m-%Y")
    if (limitedday <= paperday):
        return True
    else:
        return False


# Создание списка новостей
def get_news():
    rss_list = []
    #DataBase.open_db_connection()
    list_rss_news = DataBase.get_all_rss()
    #DataBase.close_db_connection()
    for row in list_rss_news:
        if row_days_analize(row):
            print(row)
            content = "" + row[2]
            rss_list.append([
                                f"   <b><u>{row[1]}</u></b>\n <b>Опубликовано:</b> {row[3]:%d/%m/%Y}\n <b>Сайт: {row[0]}</b>\n======================================\n{content[0:500]}",
                                row[0]])
    return rss_list


def get_news_for_person(person_id):
    rss_list = []
    #DataBase.open_db_connection()
    list_rss_news = DataBase.get_all_analized_rss(person_id)
    #DataBase.close_db_connection()
    for row in list_rss_news:
        if row_days_analize(row):
            print(row)
            content = "" + row[2]
            rss_list.append([
                                f"   <b><u>{row[1]}</u></b>\n <b>Опубликовано:</b> {row[3]:%d/%m/%Y}\n <b>Сайт: {row[0]}</b>\n======================================\n{content[0:500]}",
                                row[0]])
            #print(row[5])
    return rss_list

# Исправление ошибки с сертификатом ssl костыль просто отменяем проверку
ssl._create_default_https_context = ssl._create_unverified_context


# Регистрация оценок пользователя
def register_grades(person_name, rss_list, grade, number_of_artical, user_pages):
    global page_count
    print(str(person_name) + "___________" + str(number_of_artical))
    #DataBase.open_db_connection()
    DataBase.write_one_row_in_censors(person_name, rss_list[int(number_of_artical)][1], int(grade))
    #DataBase.close_db_connection()


# Получение статей
rss_list = get_news()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Приветсвтуем вас в телеграм боте! Данный бот предназначен для обучения путем '
                                      'чтения интересных для вас статей. Чтобы узнать о всех коммандах, напишите '
                                      '/help в чат.', None)
    #DataBase.open_db_connection()
    DataBase.insert_one_person(message.from_user.id)
    #DataBase.close_db_connection()
    time.sleep(1)


# Команда, выводящая все существующие в боте команды (кроме /start)
@bot.message_handler(commands=['help'])
def start_message(message):
    global page_count
    bot.send_message(message.chat.id, f'<b>Этот бот имеет следующие команды:</b>\n'\
                                      f'/list - вывод всех ваших RSS ссылок, на которые вы в данный момент подписаны,\n'\
                                      f'/newnews - выводится последние {page_count} новостей,\n'\
                                      f'/everydayNews - включение/выключение ежедневных новостей (пока что отключена).',
                     parse_mode="HTML")
    time.sleep(1)


# Выводим лист всех RSS подписок.
# TODO: сделать возможность удалять или дополнять этот лист RSS подписками по вводу 1й RSS ссылки
@bot.message_handler(commands=['list'])
def start_message(message):
    bot.send_message(message.chat.id, RSS_Utils.RSS_feeds(), None)
    time.sleep(1)


# Вывод следующих page_count статей
@bot.message_handler(commands=['newnews'])
def next_news(message):
    global rss_list
    global user_pages
    global page_count
    #DataBase.open_db_connection()
    user_id = DataBase.get_user_id(message.from_user.id)
    #DataBase.close_db_connection()
    switch = get_news_for_person(user_id) != []
    if switch:
        individual_list = get_news_for_person(user_id)
        print('Personal news') #для отладки TODO: убрать
    else:
        individual_list = rss_list
        print('NO personal news') #для отладки TODO: убрать
    if user_pages.get(message.from_user.id) == None:
        user_pages.update({message.from_user.id: 0})
    if (user_pages.get(message.from_user.id) + 1) * page_count < len(individual_list):
        for i in range(page_count * user_pages.get(message.from_user.id),
                       page_count * (user_pages.get(message.from_user.id) + 1)):
            keyboard = types.InlineKeyboardMarkup()
            one_k = types.InlineKeyboardButton(text='1', callback_data='1' + str(i))
            two_k = types.InlineKeyboardButton(text='2', callback_data='2' + str(i))
            three_k = types.InlineKeyboardButton(text='3', callback_data='3' + str(i))
            four_k = types.InlineKeyboardButton(text='4', callback_data='4' + str(i))
            five_k = types.InlineKeyboardButton(text='5', callback_data='5' + str(i))
            keyboard.add(one_k, two_k, three_k)
            keyboard.add(four_k, five_k)
            try:
                bot.send_message(message.chat.id, individual_list[i][0], reply_markup=keyboard, parse_mode="HTML")
                time.sleep(1)
            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL", error)
        user_pages.update({message.from_user.id: user_pages.get(message.from_user.id) + 1})
    else:
        for i in range(page_count * user_pages.get(message.from_user.id), len(individual_list)):
            keyboard = types.InlineKeyboardMarkup()
            one_k = types.InlineKeyboardButton(text='1', callback_data='1' + str(i))
            two_k = types.InlineKeyboardButton(text='2', callback_data='2' + str(i))
            three_k = types.InlineKeyboardButton(text='3', callback_data='3' + str(i))
            four_k = types.InlineKeyboardButton(text='4', callback_data='4' + str(i))
            five_k = types.InlineKeyboardButton(text='5', callback_data='5' + str(i))
            keyboard.add(one_k, two_k, three_k)
            keyboard.add(four_k, five_k)
            try:
                bot.send_message(message.chat.id, individual_list[i][0], reply_markup=keyboard, parse_mode="HTML")
                time.sleep(1)
            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL", error)
        bot.send_message(message.chat.id, "На сегодня статьи закончились!")
        user_pages.update({message.from_user.id: user_pages.get(message.from_user.id) + 1})


@bot.message_handler(commands=['everydayNews'])
def everydayNews_YN(message):
    keyboardYN = types.InlineKeyboardMarkup()
    one_k = types.InlineKeyboardButton(text='Да', callback_data='yes_everydayNews')
    two_k = types.InlineKeyboardButton(text='Нет', callback_data='no_everydayNews')
    keyboardYN.add(one_k, two_k)
    bot.send_message(message.chat.id, "Вы хотите каждый день получать рассылку новостей?", reply_markup=keyboardYN)
    time.sleep(1)


# Получаем ответ пользователя, т.е. обработка всех ответов кнопочек и всего подобного
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global rss_list
    global user_pages
    if call.data[0] in ("1", "2", "3", "4", "5"):
        register_grades(call.from_user.id, rss_list, call.data[0], call.data[1::], user_pages)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    global everydayNews

    if call.data == "yes_everydayNews":
        everydayNews = True
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Теперь каждый день в это время вам будут приходить новые статьи!')
    if call.data == "no_everydayNews":
        everydayNews = False
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Ежедневные новости отключены!')


bot.polling(none_stop=True, interval=3)
DataBase.close_db_connection()
