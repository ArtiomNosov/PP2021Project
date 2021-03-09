import DataBase
import PesronList
import telebot
from telebot import types


bot = telebot.TeleBot('1631242798:AAEBKc1x16vZpEO3QkzAecK5HEM8jE2v510')
person_name = "No_Name"
I = 0
grades_list = []


def get_news():
    rss_list = []
    DataBase.open_db_connection()
    list_rss_news = DataBase.get_last_ten_rss()
    DataBase.close_db_connection()
    for row in list_rss_news:
        print(row)
        content = "" + row[2]
        rss_list.append([f"   <b><u>{row[1]}</u></b>\n <b>Опубликовано:</b> {row[3]:%d/%m/%Y}\n <b>Сайт: {row[0]}</b>\n======================================\n{content[0:500]}", row[0]])
    return rss_list


def register_grades(person_name, rss_list, grades_list):
    PesronList.open_db_connection_p()
    for grade in range(len(grades_list)):
        PesronList.write_one_row_in_db_p(person_name, rss_list[grade][1], grades_list[grade])
    PesronList.close_db_connection_p()


rss_list = get_news()


# Регистрация пользователя по имени, т.е. запись его в глобальную переменную
@bot.message_handler(commands=['register'])
def start_message(message):
    bot.send_message(message.chat.id, "Регистрация пользователя завершена!", None)
    global person_name
    global I
    I = 0
    person_name = message.from_user.id

# Вывод новых новостей из списка и формирование списка с отценками новостей
@bot.message_handler(commands=['newnews'])
def next_news(message):
    global rss_list
    for i in range(len(rss_list)):
        keyboard = types.InlineKeyboardMarkup()
        one_k = types.InlineKeyboardButton(text='1', callback_data='1')
        two_k = types.InlineKeyboardButton(text='2', callback_data='2')
        three_k = types.InlineKeyboardButton(text='3', callback_data='3')
        four_k = types.InlineKeyboardButton(text='4', callback_data='4')
        five_k = types.InlineKeyboardButton(text='5', callback_data='5')
        keyboard.add(one_k, two_k,three_k)
        keyboard.add(four_k, five_k)

        bot.send_message(message.chat.id, rss_list[i][0], reply_markup=keyboard, parse_mode="HTML")






    #bot.send_message(message.chat.id, "На сегодня все!", reply_markup=None)
    #register_grades(person_name, rss_list, grades_list)
    #bot.send_message(message.chat.id, "Ваши оценки статей будут записаны!")

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global grades_list
    global rss_list
    if (len(grades_list) > 8) and (call.data == "1" or call.data == "2" or call.data == "3" or call.data == "4" or call.data == "5"):
        grades_list.append(call.data)
        register_grades(person_name, rss_list, grades_list)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

        grades_list = []
    elif call.data == "1" or call.data == "2" or call.data == "3" or call.data == "4" or call.data == "5":
        grades_list.append(call.data)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


    bot.send_message(call.message.chat.id, "Ваши оценка статьи записана!")



#@bot.callback_query_handler(func=lambda call: True)
#def callback_inline(call):
#    global grades_list
#    global rss_list
#    try:
#        if (len(grades_list) > 9) and (call.data == "1" or call.data == "2" or call.data == "3" or call.data == "4" or call.data == "5"):
#            grades_list.append(call.text)
#           register_grades(person_name, rss_list, grades_list)
#            bot.send_message(call.chat.id, "Все ваши оценки записаны!", reply_markup=None)
#        elif call.data == "1" or call.data == "2" or call.data == "3" or call.data == "4" or call.data == "5":
#            grades_list.append(call.text)
#    except Exception as e:
#        print(repr(e))


bot.polling()
