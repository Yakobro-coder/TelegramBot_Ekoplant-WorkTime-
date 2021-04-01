#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import telebot
from telebot import types
import gspread
from google.oauth2.service_account import Credentials


hello_text = """Приветствую, я ЭкоплантБОТ для учёта рабочего времени.
Как вас зовут, что бы я мог записать ваши рабочие часы.
"""

helper_text = """Я ЭкоплантБОТ для учёта рабочего времени.
В вашем арсенале внизу, по переменно доступны две кнопки:

- "Приступить к работе." - что бы отметиться о начале рабочего дня. При нажате этой кнопки БОТ поймёт что вы приступили к работе. 

После нажатия кнопки "Приступить к работе." у вас появится другая кнопка:  

- "Окончить рабочий день!" - для отметки о том что вы зевершили рабочий день. При нажате этой кнопки БОТ запомнит когда вы закончили работать. Не забудьте её нажать в конце дня. 
Это очень важно.

Хорошего дня!
"""


TOKEN = '1612615932:AAHMLr1gupXExX349BziuVFZRu0eSF7yLfs'
bot = telebot.TeleBot(TOKEN)


gc = gspread.service_account(filename='pythontelegrabotektoplan-dbb9bff2c140.json')
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    'pythontelegrabotektoplan-dbb9bff2c140.json',
    scopes=scopes
)
gc = gspread.authorize(credentials)
# Open a sheet from a spreadsheet in one go
google_file = gc.open("Экоплант(WorkBot)").sheet1


@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, helper_text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f'{hello_text}')
    sent = bot.send_message(message.chat.id, 'Введите пожалуйста ОЧЕНЬ внимательно ваши ФИО! :)')
    bot.register_next_step_handler(sent, menu)


def menu(message):
    message_input_name = f"""Спасибо {message.text}! Теперь вам доступен БОТ для учёта рабочего времени. Ниже у вас появилась кнопка: 

- "Приступить к работе." - для отметки начала рабочего дня.

При нажате этой кнопки БОТ поймёт что вы приступили к работе, и сразу вместо кнопки "Приступить к работе." у вас 
появится другая кнопка:  

- "Окончить рабочий день!" - для отметки окончания рабочего дня.

Кнопка "Окончить рабочий день!" запомнит когда вы закончили рабочий день. Не забудьте её нажать в конце дня.
Это очень важно. 

Хорошего дня!"""
    start_menu = types.ReplyKeyboardMarkup(True, True)
    start_menu.row('Приступить к работе')
    start_menu.row('/help')
    bot.send_message(message.chat.id, message_input_name, reply_markup=start_menu)



result_start = {}
result_stop = {}
dict_finish = {}

@bot.message_handler(commands=['result'])
def start(message):
    bot.send_message(message.chat.id, 'Запущена выгрузка данных в Google Sheets.')
    for i in range(0, len(dict_finish)):  # Вроде как записвает все данные в Google Sheets
        google_file.update(f'A{2+i}:D20', [[list(dict_finish.values())[0+i]['name'],
                                            list(dict_finish.values())[0+i]['data'],
                                            list(dict_finish.values())[0+i]['start_day'],
                                            list(dict_finish.values())[0+i]['stop_day']]])
        time.sleep(2)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    timestamp = message.date                            # Дата получения сообщение в виле unix
    value = datetime.datetime.fromtimestamp(timestamp)  # Перевод их unix в нормФормат

    dict_one = {}
    text_vivod = f'Отлично, вы приступили к работе в {value.strftime("%H:%M:%S")}!' \
                 f' Не забудьте в конце дня, отметиться о завершении рабочего дня.'
    if message.text == 'Приступить к работе':
        source_language_menu = types.ReplyKeyboardMarkup(True, True)
        source_language_menu.row('Окончить рабочий день!')
        source_language_menu.row('/help')
        bot.send_message(message.chat.id, text_vivod, reply_markup=source_language_menu)
        dict_one = {message.chat.id: {'name': f'{message.chat.first_name} {message.chat.last_name}',
                                      'data': value.strftime("%d-%m-%Y"),
                                      'start_day': value.strftime("%d-%m-%Y %H:%M:%S")}}
        result_start.update(dict_one)
        print(result_start)
    elif message.text == 'Окончить рабочий день!':
        start_menu = types.ReplyKeyboardMarkup(True, True)
        start_menu.row('Приступить к работе')
        start_menu.row('/help')
        bot.send_message(message.chat.id, f'Хорошая работа;) Рабочий день окончен в {value.strftime("%H:%M:%S")}.',
                         reply_markup=start_menu)
        dict_two = {message.chat.id: {'name': f'{message.chat.first_name} {message.chat.last_name}',
                                      'stop_day': value.strftime("%d-%m-%Y %H:%M:%S")}}
        result_stop.update(dict_two)
        print(result_stop)

    now_time = datetime.datetime.today()
    # Бэкап всех данных в Файл.txt при каждом нажатии, отдельной стракой.
    open(f'Work_time_backup {now_time.strftime("%d.%m.%Y")}.txt', 'a', encoding="utf-8").write(
        f'\n{now_time.strftime("%d.%m.%Y %H-%M-%S")} - {result_start}\n {result_stop}\n')

    # Переберает два словоря, сверяя их по ключу, создаёт новый словарь, где добовляет в словрь СТАРТ, значение 'stop-day'
    # И выводит итоговый словарь, где {id : { name, data, start_day, stop_day}

    if now_time.strftime("%H-%M") > '18-30' or now_time.strftime("%H-%M") < '07-30':
        if len(result_start) >= 1 and len(result_stop) >= 1:
            for number, key in enumerate(result_start, 0):
                for number2, key2 in enumerate(result_stop, 0):
                    if key == key2: # сверяет ключи
                        dict_stopday = {}
                        # Ниже добовляем в clen_словарь ключ stop_day со значением выданным черз .get
                        dict_stopday.update(stop_day=f"{list(result_stop.values())[number2].get('stop_day')}")
                        full_val = list(result_start.values())[number]  # Все данные из result_start
                        full_val.update(dict_stopday)                   # <- что бы потом к ним добавить stop_day
                        # Ниже совмещаем все данные из двух словорей, и записываем в итоговый словрь
                        for i in range(1, len(result_start.values())):  # ^| вида {id : { name, data, start_day, stop_day}
                            res = {key: full_val}    # Формируем id : full val
                            dict_finish.update(res)  # <-- Итоговый словарь для обработки в Google Sheets
            open(f'result_finish {now_time.strftime("%d.%m.%Y")}.txt', 'a', encoding="utf-8").write(
                f'\n{now_time.strftime("%d.%m.%Y %H-%M-%S")} - {dict_finish}\n')


bot.polling(none_stop=True)
