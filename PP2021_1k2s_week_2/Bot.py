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

grade_key = types.ReplyKeyboardMarkup(row_width=5)
button1 = types.KeyboardButton("1")
button2 = types.KeyboardButton("2")
button3 = types.KeyboardButton("3")
button4 = types.KeyboardButton("4")
button5 = types.KeyboardButton("5")
grade_key.add(button1, button2, button3, button4, button5)

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
    global grades_list
    global I
    if I == len(rss_list) - 1:
        grades_list.append(message.text)
        bot.send_message(message.chat.id, "На сегодня все!", reply_markup=None)
        register_grades(person_name, rss_list, grades_list)
        bot.send_message(message.chat.id, "Ваши оценки статей записаны!")
        I = 0
        grades_list = []
    elif (message.text == "1" or message.text == "2" or message.text == "3" or message.text == "4" or message.text == "5") and I < len(rss_list) - 1:
        grades_list.append(message.text)
        I += 1
        bot.register_next_step_handler(
            bot.send_message(message.chat.id, rss_list[I][0], reply_markup=grade_key, parse_mode="HTML"), next_news)
    elif message.text == "/newnews":
        I = 0
        bot.register_next_step_handler(
            bot.send_message(message.chat.id, rss_list[I][0], reply_markup=grade_key, parse_mode="HTML"), next_news)
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, "Введено некорректное значение!"), next_news)



bot.polling()
