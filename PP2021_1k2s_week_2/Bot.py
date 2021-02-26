import DataBase
import telebot

bot = telebot.TeleBot('1614683541:AAEk0O7u-1O6zq1wts3NfJL56i5KRLXl7oQ')


@bot.message_handler(commands=['newnews'])
def start_message(message):
    DataBase.open_db_connection()
    list_rss_news = DataBase.get_last_ten_rss()
    DataBase.close_db_connection()
    for row in list_rss_news:
        print(row)
        content = "" + row[2]
        fs = f"   <b><u>{row[1]}</u></b>\n <b>Опубликовано:</b> {row[3]:%d/%m/%Y}\n <b>Сайт: {row[4]}</b>\n======================================\n{content[0:2047]}"
        bot.send_message(message.chat.id, fs, parse_mode="HTML")
    bot.send_message(message.chat.id,"*На сегодня все ...*", parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')

bot.polling()
