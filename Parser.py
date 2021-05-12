#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import DataBase   #Библиотека для работы с базой данных. В нашем случае мы пользуемся PostgreSQL.
import xmltodict  #Используем один раз, чтобы вернуть
import xml
import xml.etree.ElementTree as ET
import feedparser
import re
import ssl
import datetime
from time import time

#import googletrans

#Исправление ошибки с сертификатом ssl костыль просто отменяем проверку
ssl._create_default_https_context = ssl._create_unverified_context

# Функция убирает теги из HTML
#def remove_html_tags(text):
#   return ''.join(xml.etree.ElementTree.fromstring(text).itertext())
def remove_html_tags(text):
   cleaner_expression = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
   clean_text = re.sub(cleaner_expression, '', text)
   return clean_text

# печатаем текущую дату и время запуска
print("Сканирование RSS запущено: " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))
# засекаем таймер выполнения
t0 = time()

# Открываем на чтение файл с фидами
try:
   opml_root = ET.parse('companies.opml.xml').getroot()
except:
   print("Ошибка открытия файла OMPL")
   sys.exit(2)

print(opml_root)
rss_count = 0


# Переводчик
#translator = googletrans.Translator()

# Соединяемся с базой данных
DataBase.open_db_connection()

# Обрабатываем все фиды (источники)
for tag in opml_root.findall('.//outline'):
   # TODO: после отладки - убрать
   #if rss_count > 1:
   #   break
   rss_url = tag.items()[2][1]
   # Прасим новости из источника rss_url
   parced = feedparser.parse(rss_url)
   # Если удачно
   if parced.status == 200:
      rss_count += 1
      print(rss_count, rss_url, parced['bozo'])
      # Сохраняем новости
      list_rss = []
      for e in parced.entries:
         # формируем список ключевых слов
         tags_str = ''
         if 'tags' in e.keys():
            for e_tag in e.tags:
               tags_str += e_tag.term
               tags_str += ";"
         # Формируем содержание
         content_str = ''
         if 'content' in e.keys():
            for e_content in e.content:
               content_str += e_content.value
         else:
            if 'summary' in e.keys():
               content_str += e.summary
         # Формируем автора
         author_str = 'None'
         if 'author' in e.keys():
            author_str = e.author
         # authors
         publisher_str = ""
         if 'authors' in e.keys():
            for e_authors in e.authors:
               if 'name' in e_authors.keys():
                  publisher_str += e_authors.name
         # Формируем дату публикации
         published_str = "Thu, 21 Sep 1900 02:20:09 GMT"
         if 'published' in e.keys():
            published_str = e.published
         # Формируем дату изменения
         updated_str = "Thu, 21 Sep 1900 02:20:09 GMT"
         if 'updated' in e.keys():
            updated_str = e.updated

         # Вывод contens на русском
         #result_rus_contents = translator.translate(remove_html_tags(content_str), src='en', dest='ru')
         #print(result_rus_contents.text)

         # Добавляем в list новую строку

         list_rss.append((xmltodict.unparse(e, full_document=False), \
                       rss_url, \
                       author_str, \
                       remove_html_tags(content_str), \
                       e.id, \
                       publisher_str, \
                       tags_str.lower(), \
                       e.title, \
                       published_str, \
                       updated_str,))
      # Записываем строки в базу
      DataBase.write_list_in_db(list_rss)
      print("===============")

# Закрываем базу данных
DataBase.close_db_connection()
# печатаем текущую дату и время остановки
print("Сканирование RSS завершено: " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))
# засекаем таймер выполнения
t1 = time()
print(f" На сканирование потрачено = {t1-t0:7.4f} секунд")

