import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import config_3, config_4
import sqlite3

#Настраиваем интерфейс логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
state = {}

conn = sqlite3.connect('calculator_db.sqlite3')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                                id INT PRIMARY KEY,
                                name TEXT,
                                last_result_calc_action TEXT,
                                last_result_calc_cel REAL,
                                last_result_calc_chisl REAL,
                                last_result_calc_znam REAL,
                                last_first_number_calc_action TEXT,
                                last_first_number_calc_cel REAL,
                                last_first_number_calc_chisl REAL,
                                last_first_number_calc_znam REAL,
                                last_second_number_calc_action TEXT,
                                last_second_number_calc_cel REAL,
                                last_second_number_calc_chisl REAL,
                                last_second_number_calc_znam REAL,
                                last_action_calc TEXT);''')
conn.commit()

def checking_for_positivity(result):
    if result[0] < 0:
        result[0] *= -1
    if result[1] < 0:
        result[1] *= -1
    return result

def bigger_smaller(first_num, second_num):
    return (first_num[0] * first_num[2] + first_num[1]) * second_num[2] > \
           (second_num[0] * second_num[2] + second_num[1]) * first_num[2]

def subtraction(first_num, second_num):
    result = [0,
              (first_num[0] * first_num[2] + first_num[1]) * second_num[2] -
              (second_num[0] * second_num[2] + second_num[1]) * first_num[2],
              first_num[2] * second_num[2],
              '']
    print(result)
    result = checking_for_positivity(result)
    if result[1] >= result[2]:
        result[0] += result[1] // result[2]
        result[1] -= result[2] * (result[1] // result[2])
    print(result)
    return result

def addition(first_num, second_num):
    result = [0,
              (first_num[0] * first_num[2] + first_num[1]) * second_num[2] +
              (second_num[0] * second_num[2] + second_num[1]) * first_num[2],
              first_num[2] * second_num[2],
              '']
    print(result)
    result = checking_for_positivity(result)
    if result[1] >= result[2]:
        result[0] += result[1] // result[2]
        result[1] -= result[2] * (result[1] // result[2])
    print(result)
    return result

def sokrashenie(result_1, result_2, s):
    i = 2
    while i <= (int(result_2) // 2):
        if result_2 % i == 0 and result_1 % i == 0:
            result_2 /= i
            result_1 /= i
            s += 2
        i += 1
    s -= 1
    return result_1, result_2, s

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['/nod', '/nok'], ['/sort', '/calc']]
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите действие", reply_markup=ReplyKeyboardMarkup(keyboard,
                                                                                              resize_keyboard=True,
                                                                                              one_time_keyboard=True))
    state[update.effective_user.id] = {'dia_stat': 0}

async def sort(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]['dia_stat'] = 'sort_1'
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите числа, чтобы я их отсортировал")

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]['dia_stat'] = 1
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Введите первое число, если число дробное, то дробную часть отделите от целой пробелом, при её записи используте /. Вот пример записи 5 5/6 или 0 2/7")

async def nod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]['dia_stat'] = 'nod_1'
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Введите 2 целых числа, чтобы я сказал вам их НОД")

async def nok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]['dia_stat'] = 'nok_1'
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Введите 2 целых числа, чтобы я сказал вам их НОК")

async def message_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if state[update.effective_user.id]['dia_stat'] == 'sort_1':
        keyboard = [['по возрастанию', 'по убыванию']]
        state[update.effective_user.id]['numbers_sort'] = update.effective_message.text.split(' ')
        state[update.effective_user.id]['dia_stat'] = 'sort_2'
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Как нужно отсортировать?",
                                       reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                        one_time_keyboard=True))
    elif state[update.effective_user.id]['dia_stat'] == 'sort_2':
        state[update.effective_user.id]['how_sort'] = update.effective_message.text
        state[update.effective_user.id]['dia_stat'] = 'sort_0'
        how_sort = state[update.effective_user.id]['how_sort']
        new_numbers_sort = []
        new_numbers_sort_str = []
        old_numbers_sort = [state[update.effective_user.id]['numbers_sort']]
        for symbol in old_numbers_sort[0]:
            if float(symbol) % 1 == 0:
                symbol = int(symbol)
            else:
                symbol = float(symbol)
            new_numbers_sort.append(symbol)
        print(new_numbers_sort, how_sort)
        for i in range(len(new_numbers_sort)-1):
            for j in range(len(new_numbers_sort) - 1):
                first_num_sort = new_numbers_sort[j]
                second_num_sort = new_numbers_sort[j+1]
                if how_sort == 'по убыванию':
                    if second_num_sort > first_num_sort:
                        new_numbers_sort[j] = second_num_sort
                        new_numbers_sort[j + 1] = first_num_sort
                elif how_sort == 'по возрастанию':
                    if second_num_sort < first_num_sort:
                        new_numbers_sort[j] = second_num_sort
                        new_numbers_sort[j + 1] = first_num_sort
        for symbol in new_numbers_sort:
            symbol = str(symbol)
            new_numbers_sort_str.append(symbol)
        text = ' '.join(new_numbers_sort_str)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    if state[update.effective_user.id]['dia_stat'] == 'nod_1':
        numbers_nod = update.effective_message.text.split(' ')
        if float(numbers_nod[0]) % 1 != 0 or float(numbers_nod[1]) % 1 != 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Введите 2 целых числа')
            await nod(update, context)
        else:
            new_numbers_nod = [int(numbers_nod[0]), int(numbers_nod[1])]
            max_nod = 0
            if new_numbers_nod[0] >= 1000000 or new_numbers_nod[1] >= 1000000:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text='Введите 2 числа поменьше, чтобы не нагружать сервер')
                await nod(update, context)
            else:
                for i in range(1, min(new_numbers_nod) + 1):
                    if new_numbers_nod[0] % i == 0 and new_numbers_nod[1] % i == 0:
                        max_nod = i
                state[update.effective_user.id]['dia_stat'] = 0
                await context.bot.send_message(chat_id=update.effective_chat.id, text=max_nod)

    if state[update.effective_user.id]['dia_stat'] == 'nok_1':
        numbers_nok = update.effective_message.text.split(' ')
        if float(numbers_nok[0]) % 1 != 0 or float(numbers_nok[1]) % 1 != 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Введите 2 целых числа')
            await nok(update, context)
        else:
            new_numbers_nok = [int(numbers_nok[0]), int(numbers_nok[1])]
            if new_numbers_nok[0] > 1000 or new_numbers_nok[1] > 1000:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text='Введите 2 числа поменьше, чтобы не нагружать сервер')
                await nok(update, context)
            else:
                min_nok = 0
                first_number = new_numbers_nok[0]
                second_number = new_numbers_nok[1]
                first_number_copy = first_number
                second_number_copy = second_number
                first_lst = [first_number]
                second_lst = [second_number]
                run = True
                while run:
                    for symbol_f_nok in first_lst:
                        for symbol_s_nok in second_lst:
                            if symbol_f_nok == symbol_s_nok:
                                min_nok = symbol_f_nok
                                run = False
                    first_number += first_number_copy
                    second_number += second_number_copy
                    first_lst.append(first_number)
                    second_lst.append(second_number)
                state[update.effective_user.id]['dia_stat'] = 0
                await context.bot.send_message(chat_id=update.effective_chat.id, text=min_nok)

    if state[update.effective_user.id]['dia_stat'] == 1:
        lst = update.effective_message.text.split(' ')
        cel_1 = int(lst[0])
        if update.effective_message.text[0] == '-':
            first_plus = False
        else:
            first_plus = True
        print(lst)
        if len(lst) == 2:
            drob = lst[1].split('/')
            chisl_1 = int(drob[0])
            znamen_1 = int(drob[1])
            state[update.effective_user.id]['first_num'] = [cel_1, chisl_1, znamen_1, first_plus]
            # state[update.effective_user.id]['first_num'] = int(lst[0]) + int(drob[0]) * (1/int(drob[1]))
        if len(lst) == 1 or (len(lst) == 2 and int(lst[1].split('/')[1]) == 0):
            state[update.effective_user.id]['first_num'] = [cel_1, 0, 1, first_plus]
        print(update.effective_message.text)
        state[update.effective_user.id]['dia_stat'] = 2
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите второе число ")

    elif state[update.effective_user.id]['dia_stat'] == 2:
        lst_2 = update.effective_message.text.split(' ')
        cel_2 = int(lst_2[0])
        if update.effective_message.text[0] == '-':
            second_plus = False
        else:
            second_plus = True
        print(lst_2)
        if len(lst_2) == 2:
            drob = lst_2[1].split('/')
            chisl_2 = int(drob[0])
            znamen_2 = int(drob[1])
            state[update.effective_user.id]['second_num'] = [cel_2, chisl_2, znamen_2, second_plus]
            # state[update.effective_user.id]['second_num'] = int(lst[0]) + int(drob[0]) * (1 / int(drob[1]))
        if len(lst_2) == 1 or (len(lst_2) == 2 and int(lst_2[1].split('/')[1]) == 0):
            state[update.effective_user.id]['second_num'] = [cel_2, 0, 1, second_plus]
        print(update.effective_message.text)
        state[update.effective_user.id]['dia_stat'] = 3
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите знак ")

    elif state[update.effective_user.id]['dia_stat'] == 3:
        first_num = state[update.effective_user.id]['first_num']
        second_num = state[update.effective_user.id]['second_num']
        state[update.effective_user.id]['action'] = update.effective_message.text
        action = state[update.effective_user.id]['action']
        if first_num[0] >= 1000000000000000000000000000 or second_num[0] >= 1000000000000000000000000000:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Введите 2 числа поменьше, чтобы не нагружать сервер')
            await calc(update, context)
        else:
            print(state[update.effective_user.id]['action'])
            print(first_num, second_num)
            result = []
            if not first_num[3]:
                first_num[0] *= -1
            if not second_num[3]:
                second_num[0] *= -1
            if state[update.effective_user.id]['action'] == '+':
                if first_num[3] and second_num[3]:
                    result = addition(first_num, second_num)
                elif first_num[3]:
                    result = subtraction(first_num, second_num)
                    if not bigger_smaller(first_num, second_num):
                        result[3] = '-'
                elif second_num[3]:
                    result = subtraction(first_num, second_num)
                    if bigger_smaller(first_num, second_num):
                        result[3] = '-'
                else:
                    result = addition(first_num, second_num)
                    result[3] = '-'
            elif state[update.effective_user.id]['action'] == '-':
                if first_num[3] and second_num[3]:
                    result = subtraction(first_num, second_num)
                    if not bigger_smaller(first_num, second_num):
                        result[3] = '-'
                elif first_num[3]:
                    result = addition(first_num, second_num)
                elif second_num[3]:
                    result = addition(first_num, second_num)
                    result[3] = '-'
                else:
                    result = subtraction(first_num, second_num)
                    if bigger_smaller(first_num, second_num):
                        result[3] = '-'
            elif state[update.effective_user.id]['action'] == '*':
                result = [0,
                          (first_num[1] + first_num[0] * first_num[2]) * (
                                      second_num[1] + second_num[0] * second_num[2]),
                          first_num[2] * second_num[2],
                          '']
                if result[1] >= result[2]:
                    result[0] += result[1] // result[2]
                    result[1] -= result[2] * (result[1] // result[2])
                if (first_num[3] and not second_num[3]) or (not first_num[3] and second_num[3]):
                    result[3] = '-'
            elif state[update.effective_user.id]['action'] in ['/', ':']:
                result = [0,
                          (first_num[1]+first_num[0]*first_num[2])*(second_num[2]),
                          (first_num[2]) * (second_num[1]+second_num[0]*second_num[2]),
                          '']
                if result[1] >= result[2]:
                    result[0] += result[1] // result[2]
                    result[1] -= result[2] * (result[1] // result[2])
                if (first_num[3] and not second_num[3]) or (not first_num[3] and second_num[3]):
                    result[3] = '-'

            print(result)

            if result[0] >= 0 and result[1] < 0:
                result[1] *= -1
                result[3] = '-'

            if int(result[1]) // 2 >= 5000000:
                text = f'Мы не можем сократить полученый нами результат, ' \
                       f'т.к числитель или знаменатель вводных чисел слишком большой.' \
                       f'Однако мы можем сказать вам не сокращенную дробь. {result[3]}{result[0]} {result[1]}/{result[2]}'
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=text)
            else:
                s = 2
                sokr = sokrashenie(result[1], result[2], s)
                result[1] = sokr[0]
                result[2] = sokr[1]
                s = sokr[2]
                while s > 1:
                    sokr = sokrashenie(result[1], result[2], s)
                    result[1] = sokr[0]
                    result[2] = sokr[1]
                    s = sokr[2]
                if int(sokr[0]) == 0:
                    text = f'{result[3]}{result[0]}'
                else:
                    text = f'{result[3]}{result[0]} {int(sokr[0])}/{int(sokr[1])}'
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            if first_num[3]:
                first_num_action = '+'
            else:
                first_num_action = '-'
            if second_num[3]:
                second_num_action = '+'
            else:
                second_num_action = '-'
            if result[3] == '-':
                result_action = '-'
            else:
                result_action = '+'
            cursor.execute(f'SELECT id, name FROM users WHERE id = {update.effective_user.id}')
            data = cursor.fetchone()
            elements = [
                result_action,
                result[0],
                result[1],
                result[2],
                first_num_action,
                first_num[0],
                first_num[1],
                first_num[2],
                second_num_action,
                second_num[0],
                second_num[1],
                second_num[2],
                action,
                update.effective_user.id,
            ]

            if data:
                cursor.execute(
                    """UPDATE users SET last_result_calc_action = ?,
                                last_result_calc_cel = ?,
                                last_result_calc_chisl = ?, 
                                last_result_calc_znam = ?, 
                                last_first_number_calc_action = ?,
                                last_first_number_calc_cel = ?, 
                                last_first_number_calc_chisl = ?, 
                                last_first_number_calc_znam = ?, 
                                last_second_number_calc_action = ?,
                                last_second_number_calc_cel = ?, 
                                last_second_number_calc_chisl = ?, 
                                last_second_number_calc_znam = ?, 
                                last_action_calc = ?
                                WHERE id = ?
                                """,
                    elements,
                )
            else:
                cursor.execute(
                    f'INSERT INTO users VALUES({update.effective_user.id}, "{update.effective_user.username}", '
                    f'"{result_action}",{result[0]}, {result[1]}, {result[2]}, "{first_num_action}", {first_num[0]},'
                    f'{first_num[1]}, {first_num[2]}, "{second_num_action}", {second_num[0]}, {second_num[1]}, '
                    f'{second_num[2]}, "{action}")')
            conn.commit()

# cursor.execute('''CREATE TABLE IF NOT EXISTS users(
#                                 id INT PRIMARY KEY,
#                                 name TEXT,
#                                 last_result_calc_action TEXT,
#                                 last_result_calc_cel REAL,
#                                 last_result_calc_chisl REAL,
#                                 last_result_calc_znam REAL,
#                                 last_first_number_calc_action TEXT,
#                                 last_first_number_calc_cel REAL,
#                                 last_first_number_calc_chisl REAL,
#                                 last_first_number_calc_znam REAL,
#                                 last_second_number_calc_action TEXT,
#                                 last_second_number_calc_cel REAL,
#                                 last_second_number_calc_chisl REAL,
#                                 last_second_number_calc_znam REAL,
#                                 last_action_calc TEXT);''')

# config_4['token'] calc
# config_3['token'] test

if __name__ == '__main__':
    application = ApplicationBuilder().token(config_4['token']).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    calc_handler = CommandHandler('calc', calc)  # Создаю обработчик команд
    application.add_handler(calc_handler)

    nod_handler = CommandHandler('nod', nod)
    application.add_handler(nod_handler)

    nok_handler = CommandHandler('nok', nok)
    application.add_handler(nok_handler)

    sort_handler = CommandHandler('sort', sort)
    application.add_handler(sort_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_processing)
    application.add_handler(message_handler)

    application.run_polling()