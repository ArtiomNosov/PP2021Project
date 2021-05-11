# # -*- coding: utf-8 -*-
#
# import smtplib  #для работы с почтой по протоколу SMTP
# import os   #для работы с операционной системой
# from email.mime.multipart import MIMEMultipart  #используется для отправки сообщений в двух форматах text и html
# from email.mime.text import MIMEText    #с помощью него задаём формат сообщения
# from email.mime.base import MIMEBase    #с помощью него будем добавлять вложение в письмо
# from email import encoders  #для преобразования файла перед его отправкой
# from platform import python_version #для определения версии python
# import ssl  #только для отмены проверки ssl
#
# #Исправление ошибки с сертификатом ssl костыль просто отменяем проверку
# #context = ssl._create_unverified_context()
# ssl._create_default_https_context = ssl._create_unverified_context
#
# server = 'smtp.gmail.com' #стандартный почтовый адрес smtp
# user = 'ksuha.noso@gmail.com'  #мой почтовый ящик
# password = '***'    #мой ***
#
# recipients = ['eveonlineaukcionerbariga1@mail.ru', 'artiom-nj@mial.ru']
# sender = 'ksuha.noso@gmail.com'
# subject = 'Тема сообщения'
# text = 'Текст сообщения'
# html = '<html><head></head><body><p>' + text + '</p></body></html>'
#
# filepath = "C:/Users/Artiom/Documents/SolvePsihology.pdf"
# basename = os.path.basename(filepath)   #извлекаем имя файла отбрасываем путь
# filesize = os.path.getsize(filepath)    #расчитываем размер файла
#
# msg = MIMEMultipart('alternative')  #конструируем многокомпонентный объект
# msg['Subject'] = subject
# msg['From'] = 'Python script <' + sender + '>'
# msg['To'] = ', '.join(recipients)
# msg['Reply-To'] = sender
# msg['Return-Path'] = sender
# msg['X-Mailer'] = 'Python/' + (python_version())
#
# part_text = MIMEText(text, 'plain') #Формируем тело в текстовом формате.
# part_html = MIMEText(html, 'html')  #Формируем тело в формате html.
# part_file = MIMEBase('application', 'octet-stream; name="{}"'.format(basename)) #Формируем тело для вложения.
# part_file.set_payload(open(filepath, "rb").read())  #Загружаем в тело письма файл.
# part_file.add_header('Content-Description', basename)   #Добавляем заголовок к Content-Description контентной части письма. Указываем просто имя файла.
# part_file.add_header('Content-Disposition', 'attachment; filename="{}"; size={}'.format(basename, filesize))    #Добавляем заголовок к Content-Disposition контентной части письма. Указываем имя файла и его размер.
# encoders.encode_base64(part_file)   #Кодируем файл в base64.
#
# msg.attach(part_text)   #Присоединяем к письму сформированное тело в текстовом формате.
# msg.attach(part_html)   #Присоединяем к письму сформированное тело в формате html.
# msg.attach(part_file)   #Присоединяем к письму сформированное тело с вложением.

# mail = smtplib.SMTP_SSL(server, 465) #Создаем SMTP сессию по защищенному протоколу с сервером отправки. Саму сессию записываем в переменную mail, по которой можно будем обращаться к объектам smtplib. Полный их перечень можно найти в документации python. если нам необходимо создать незащищенную сессию, то можно заменить строку на mail = smtplib.SMTP(server, 25), где 25 — стандартный порт для отправки почты.
# mail.login(user, password)
# mail.sendmail(sender, recipients, msg.as_string())  #Отправляем письмо.
# mail.quit() #Закрываем сессию.



# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import imaplib
import email

def getMail_list():
    result = {}

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('ksuha.noso@gmail.com', '89huj6gh6hJHvc6dvf5dV76erder2342GV665Ggy7ertr6vghTY6yijpZQjKJ6gfFGt6554edQW556645GF67y')

    mail.list()
    mail.select("inbox")

    ###

    result, data = mail.search(None, "ALL")

    ids = data[0]
    id_list = ids.split()
    latest_email_id = id_list[-1]

    result, data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = data[0][1]
    raw_email_string = raw_email.decode('utf-8')

    ###


    email_message = email.message_from_string(raw_email_string)

    print(email_message['To'])
    print(email.utils.parseaddr(email_message['From']))
    print(email_message['Date'])
    print(email_message['Subject'])
    print(email_message['Message-Id'])

    ###

    email_message = email.message_from_string(raw_email_string)

    if email_message.is_multipart():
        for payload in email_message.get_payload():
            body = payload.get_payload(decode=True).decode('utf-8')
            print(body)
            result.append(body)
    else:
        body = email_message.get_payload(decode=True).decode('utf-8')
        print(body)
        result.append(body)

    return result