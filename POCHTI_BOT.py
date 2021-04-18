#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import pytz
import telebot
from telebot import types
import gspread
from google.oauth2.service_account import Credentials



hello_text = """Приветствую, я ЭкоплантБОТ для учёта рабочего времени.

"""

helper_text = """Я ЭкоплантБОТ для учёта рабочего времени.
В вашем арсенале внизу, по переменно доступны две кнопки:

- "Приступить к работе." - что бы отметиться о начале рабочего дня. При нажате этой кнопки БОТ поймёт что вы приступили к работе. 

После нажатия кнопки "Приступить к работе." у вас появится другая кнопка:  

- "Окончить рабочий день!" - для отметки о том что вы зевершили рабочий день. При нажате этой кнопки БОТ запомнит когда вы закончили работать. Не забудьте её нажать в конце дня. 
Это очень важно.

Хорошего дня!
"""

# Чтение токена из файла
with open('token.txt', encoding='utf-8') as f:
    TOKEN = f.read()


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, helper_text)


@bot.message_handler(commands=['exel'])
def start(message):
    bot.send_message(message.chat.id, 'https://docs.google.com/spreadsheets/d/1GjhzvK6vgP0m8EYrcbPeYuJOfYy40GUQ6DqLKqxV838/edit#gid=0')


@bot.message_handler(commands=['testwork'])
def start(message):
    bot.send_message(message.chat.id, 'Бот в сети! Бот работает!')


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f'{hello_text}')
    message_input_name = f"""Теперь вам доступен БОТ для учёта рабочего времени. Ниже у вас появилась кнопка: 

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


@bot.message_handler(content_types=['text'])
def handle_text(message):
    timestamp = message.date                            # Дата получения сообщение в виле unix
    unixi = datetime.datetime.fromtimestamp(timestamp)  # Перевод их unix в нормФормат
    value = unixi.now(pytz.timezone('Europe/Moscow'))
    value.date()


    dict_one = {}
    text_vivod = f'Отлично, вы приступили к работе в {value.strftime("%H:%M:%S")}!' \
                 f' Не забудьте в конце дня, отметиться о завершении рабочего дня.'

    if message.text == 'Приступить к работе' and value.strftime("%d.%m.%Y") != result_start[message.chat.id]['data']:
        global result_start
        result_start = {}

    if message.text == 'Приступить к работе' and message.chat.id not in result_start.keys():
        source_language_menu = types.ReplyKeyboardMarkup(True, True)
        source_language_menu.row('Окончить рабочий день!')
        source_language_menu.row('/help')
        bot.send_message(message.chat.id, text_vivod, reply_markup=source_language_menu)
        dict_one = {message.chat.id: {'name': f'{message.chat.first_name} {message.chat.last_name}',
                                      'data': value.strftime("%d.%m.%Y"),
                                      'start_day': value.strftime("%H:%M")}}
        result_start.update(dict_one)
        print(result_start)
    elif message.text == 'Приступить к работе' and message.chat.id in result_start.keys():
        bot.send_message(message.chat.id, 'Вы не можете дважды за день приступить к началу рабочего дня.')

    elif message.text == 'Окончить рабочий день!':
        start_menu = types.ReplyKeyboardMarkup(True, True)
        start_menu.row('Приступить к работе')
        start_menu.row('/help')
        bot.send_message(message.chat.id, f'Хорошая работа;) Рабочий день окончен в {value.strftime("%H:%M:%S")}.',
                         reply_markup=start_menu)
        dict_two = {message.chat.id: {'stop_day': value.strftime("%H:%M")}}
        result_stop.update(dict_two)
        for number, key in enumerate(result_start, 0):
            for number2, key2 in enumerate(result_stop, 0):
                if key == key2:  # сверяет ключи
                    dict_stopday = {}
                    # Ниже добовляем в clen_словарь ключ stop_day со значением выданным черз .get
                    dict_stopday.update(stop_day=f"{list(result_stop.values())[number2].get('stop_day')}")
                    full_val = list(result_start.values())[number]  # Все данные из result_start
                    full_val.update(dict_stopday)  # <- что бы потом к ним добавить stop_day
                    # Ниже совмещаем все данные из двух словорей, и записываем в итоговый словрь
                    for i in range(1, len(result_start.values())):  # ^| вида {id : { name, data, start_day, stop_day}
                        res = {key: full_val}  # Формируем id : full val
                        result_start.update(res)  # <-- Итоговый словарь для обработки в Google Sheets
        print(result_start)

    now_time = datetime.datetime.today()
    # Бэкап всех данных в Файл.txt при каждом нажатии, отдельной стракой.
    with open(f'Work_time_backup_{now_time.strftime("%d.%m.%Y")}.txt', 'a', encoding="utf-8") as backup:
        backup.write(f'\n{now_time.strftime("%d.%m.%Y %H-%M-%S")} - {result_start}')

    update_sheets()

# Записываем номер строки в файл, что бы при подении всегда помнить где была последння
# строка с датой(та что зелённая)
# Здесь мы берём число из файла(там всегда цифра) и str переводим в int
with open(f'Number_line.txt', 'r', encoding="utf-8") as doc:
    numb = doc.read()
    numb = int(numb)
def update_sheets():
    now_time = datetime.datetime.today()
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

    # Показывает номер первой пустой строки проверев документ.
    # numb = (len(google_file.get_all_values()) + 1)
    global numb
    print(numb)


    if google_file.acell(f'A{numb}').value == now_time.strftime("%d.%m.%Y"):
        # Объеденяет ячейку в одну
        spreadsheetId = "1GjhzvK6vgP0m8EYrcbPeYuJOfYy40GUQ6DqLKqxV838"
        sheetName = "Лист номер один"
        client = gspread.authorize(credentials)
        ss = client.open_by_key(spreadsheetId)
        sheetId = ss.worksheet(sheetName)._properties['sheetId']
        body = {
            "requests": [
                {
                    "mergeCells": {
                        "mergeType": "MERGE_ALL",
                        "range": {  # In this sample script, all cells of (пример)"A4:C4" of "Sheet1" are merged.
                            "sheetId": sheetId,
                            "startRowIndex": numb - 1,
                            "endRowIndex": numb,
                            "startColumnIndex": 0,
                            "endColumnIndex": 3
                        }
                    }
                }
            ]
        }
        res = ss.batch_update(body)
        # Задаёт ФОРМАТ ячейкам под дату(цвет и жир)
        google_file.format(f'A{numb}', {'textFormat': {'bold': True}})  # Dелает жирным текст
        google_file.format(f"A{numb}:C{numb}", {
            "backgroundColor": {
                "red": 0.750,
                "green": 0.900,
                "blue": 0.750,
                "alpha": 1.0
            },
            "horizontalAlignment": "CENTER",
            "textFormat": {
                "foregroundColor": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                },
                "fontSize": 10,
                "bold": True
            }
        })

        google_file.update(f'A{numb}', now_time.strftime("%d.%m.%Y"))
        print((result_start.values()))
        for i in range(0, len(result_start)):  # Вроде как записвает все данные в Google Sheets
            if len(list(result_start.values())[0+i]) == 3:
                google_file.update(f'A{numb+1+i}:C3000', [[list(result_start.values())[0+i]['name'],
                                                           list(result_start.values())[0+i]['start_day']]])
                time.sleep(2)
            else:
                google_file.update(f'A{numb + 1 + i}:C3000', [[list(result_start.values())[0 + i]['name'],
                                                               list(result_start.values())[0 + i]['start_day'],
                                                               list(result_start.values())[0 + i]['stop_day']]])
                time.sleep(2)

    elif google_file.acell(f'A{numb}').value != now_time.strftime("%d.%m.%Y"):
        numb = (len(google_file.get_all_values()) + 1)
        with open(f'Number_line.txt', 'w', encoding="utf-8") as doc:
            doc.write(str(numb))
        print(numb)
        # Объеденяет ячейку в одну
        spreadsheetId = "1GjhzvK6vgP0m8EYrcbPeYuJOfYy40GUQ6DqLKqxV838"
        sheetName = "Лист номер один"
        client = gspread.authorize(credentials)
        ss = client.open_by_key(spreadsheetId)
        sheetId = ss.worksheet(sheetName)._properties['sheetId']
        body = {
            "requests": [
                {
                    "mergeCells": {
                        "mergeType": "MERGE_ALL",
                        "range": {  # In this sample script, all cells of (пример)"A4:C4" of "Sheet1" are merged.
                            "sheetId": sheetId,
                            "startRowIndex": numb - 1,
                            "endRowIndex": numb,
                            "startColumnIndex": 0,
                            "endColumnIndex": 3
                        }
                    }
                }
            ]
        }
        res = ss.batch_update(body)
        # Задаёт ФОРМАТ ячейкам под дату(цвет и жир)
        google_file.format(f'A{numb}', {'textFormat': {'bold': True}})  # Dелает жирным текст
        google_file.format(f"A{numb}:C{numb}", {
            "backgroundColor": {
                "red": 0.750,
                "green": 0.900,
                "blue": 0.750,
                "alpha": 1.0
            },
            "horizontalAlignment": "CENTER",
            "textFormat": {
                "foregroundColor": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                },
                "fontSize": 10,
                "bold": True
            }
        })

        google_file.update(f'A{numb}', now_time.strftime("%d.%m.%Y"))
        print((result_start.values()))
        for i in range(0, len(result_start)):  # Вроде как записвает все данные в Google Sheets
            if len(list(result_start.values())[0 + i]) == 3:
                google_file.update(f'A{numb + 1 + i}:C3000', [[list(result_start.values())[0 + i]['name'],
                                                               list(result_start.values())[0 + i]['start_day']]])
                time.sleep(2)
            else:
                google_file.update(f'A{numb + 1 + i}:C3000', [[list(result_start.values())[0 + i]['name'],
                                                               list(result_start.values())[0 + i]['start_day'],
                                                               list(result_start.values())[0 + i]['stop_day']]])
                time.sleep(2)


bot.polling(none_stop=True)
