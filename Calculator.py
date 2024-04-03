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

def arithmetic_operations(first_num, second_num, action):
    result = []
    if not first_num[3]:
        first_num[0] *= -1
    if not second_num[3]:
        second_num[0] *= -1
    if action == '+':
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
    elif action == '-':
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
    elif action == '*':
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
    elif action in ['/', ':']:
        result = [0,
                  (first_num[1] + first_num[0] * first_num[2]) * (second_num[2]),
                  (first_num[2]) * (second_num[1] + second_num[0] * second_num[2]),
                  '']
        if result[1] >= result[2]:
            result[0] += result[1] // result[2]
            result[1] -= result[2] * (result[1] // result[2])
        if (first_num[3] and not second_num[3]) or (not first_num[3] and second_num[3]):
            result[3] = '-'
    return result

def znam(num):
    return len(num.split('/')) == 1

def checking_for_positivity(result):
    if result[0] < 0:
        result[0] *= -1
    if result[1] < 0:
        result[1] *= -1
    return result

def bigger_smaller(first_num, second_num):
    first_num = checking_for_positivity(first_num)
    second_num = checking_for_positivity(second_num)
    return (first_num[0] * first_num[2] + first_num[1]) * second_num[2] > \
           (second_num[0] * second_num[2] + second_num[1]) * first_num[2]

def subtraction(first_num, second_num):
    first_num = checking_for_positivity(first_num)
    second_num = checking_for_positivity(second_num)
    result = [0,
              (first_num[0] * first_num[2] + first_num[1]) * second_num[2] -
              (second_num[0] * second_num[2] + second_num[1]) * first_num[2],
              first_num[2] * second_num[2],
              '']
    result = checking_for_positivity(result)
    if result[1] >= result[2]:
        result[0] += result[1] // result[2]
        result[1] -= result[2] * (result[1] // result[2])
    return result

def addition(first_num, second_num):
    first_num = checking_for_positivity(first_num)
    second_num = checking_for_positivity(second_num)
    result = [0,
              (first_num[0] * first_num[2] + first_num[1]) * second_num[2] +
              (second_num[0] * second_num[2] + second_num[1]) * first_num[2],
              first_num[2] * second_num[2],
              '']
    result = checking_for_positivity(result)
    if result[1] >= result[2]:
        result[0] += result[1] // result[2]
        result[1] -= result[2] * (result[1] // result[2])
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
                                   text="Введите пример, если число дробное, то дробную часть отделите от целой пробелом, при её записи используте /. Вот пример записи 5 5/6 - 0 2/7")

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
        # Ввод
        lst = update.effective_message.text.split(' ')
        state[update.effective_user.id]['count_numbers'] = (1 + lst.count('-') + lst.count('+') + lst.count('/') +
                                                            lst.count(':') + lst.count('*'))
        numbers_lst = []
        for i in range(len(lst)):
            if lst[i] not in ['+', '-', '/', ':', '*']:
                numbers_lst.append(lst[i])

        actions_lst = []
        for i in range(len(lst)):
            if lst[i] in ['+', '-', '/', ':', '*']:
                actions_lst.append(lst[i])
            else:
                actions_lst.append(None)

        len_numbers = []
        len_number = 0
        for i in range(len(actions_lst)):
            if actions_lst[i]:
                len_numbers.append(len_number - 1)
            else:
                len_number += 1
        len_numbers.append(len_number - 1)

        int_numbers_lst = [[] for i in range(len(len_numbers))]
        new_numbers_lst = [[] for i in range(len(len_numbers))]
        calc_numbers_lst = [[] for i in range(len(len_numbers))]
        calc_actions = []

        run = True
        o = 0
        for i in range(len(len_numbers)):
            run = True
            while o < len(numbers_lst) and run:
                new_numbers_lst[i].append(numbers_lst[o])
                if o == len_numbers[i]:
                    run = False
                o += 1

        for i in range(len(new_numbers_lst)):
            for j in range(len(new_numbers_lst[i])):
                if znam(new_numbers_lst[i][j]):
                    int_numbers_lst[i].append(new_numbers_lst[i][j])
                else:
                    int_numbers_lst[i].append(new_numbers_lst[i][j].split('/')[0])
                    int_numbers_lst[i].append(new_numbers_lst[i][j].split('/')[1])

        for i in range(len(new_numbers_lst)):
            if len(int_numbers_lst[i]) == 3:
                calc_numbers_lst[i] = [int_numbers_lst[i][0], int_numbers_lst[i][1], int_numbers_lst[i][2], '']
            elif len(int_numbers_lst[i]) == 1:
                calc_numbers_lst[i] = [int_numbers_lst[i][0], '0', '1', '']
            elif len(int_numbers_lst[i]) == 2:
                calc_numbers_lst[i] = ['0', int_numbers_lst[i][0], int_numbers_lst[i][1], '']
            if calc_numbers_lst[i][0][0] == '-' or calc_numbers_lst[i][1][0] == '-':
                calc_numbers_lst[i][3] = False
            else:
                calc_numbers_lst[i][3] = True
            calc_numbers_lst[i] = [int(calc_numbers_lst[i][0]), int(calc_numbers_lst[i][1]),
                                   int(calc_numbers_lst[i][2]), calc_numbers_lst[i][3]]
            calc_numbers_lst[i] = checking_for_positivity(calc_numbers_lst[i])

        for i in range(len(actions_lst)):
            if actions_lst[i]:
                calc_actions.append(actions_lst[i])




        # Арифметические действия
        print(calc_numbers_lst)
        print(calc_actions)
        problem = False
        for i in range(len(calc_numbers_lst)):
            if calc_numbers_lst[i][0] >= 1000000000000000000000000000:
                problem = True
        if problem:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Введите пример с 2 числами поменьше, чтобы не нагружать сервер')
            await calc(update, context)
        else:
            j = 0
            result = []
            first_num = calc_numbers_lst[0]
            while j < len(calc_actions):
                second_num = calc_numbers_lst[j + 1]
                result = arithmetic_operations(first_num, second_num, calc_actions[j])
                if result[3] == '-':
                    first_num = [result[0], result[1], result[2], False]
                else:
                    first_num = [result[0], result[1], result[2], True]
                j += 1
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
            # if first_num[3]:
            #     first_num_action = '+'
            # else:
            #     first_num_action = '-'
            # if second_num[3]:
            #     second_num_action = '+'
            # else:
            #     second_num_action = '-'
            # if result[3] == '-':
            #     result_action = '-'
            # else:
            #     result_action = '+'
            # cursor.execute(f'SELECT id, name FROM users WHERE id = {update.effective_user.id}')
            # data = cursor.fetchone()
            # elements = [
            #     result_action,
            #     result[0],
            #     result[1],
            #     result[2],
            #     first_num_action,
            #     first_num[0],
            #     first_num[1],
            #     first_num[2],
            #     second_num_action,
            #     second_num[0],
            #     second_num[1],
            #     second_num[2],
            #     action,
            #     update.effective_user.id,
            # ]
            #
            # if data:
            #     cursor.execute(
            #         """UPDATE users SET last_result_calc_action = ?,
            #                     last_result_calc_cel = ?,
            #                     last_result_calc_chisl = ?,
            #                     last_result_calc_znam = ?,
            #                     last_first_number_calc_action = ?,
            #                     last_first_number_calc_cel = ?,
            #                     last_first_number_calc_chisl = ?,
            #                     last_first_number_calc_znam = ?,
            #                     last_second_number_calc_action = ?,
            #                     last_second_number_calc_cel = ?,
            #                     last_second_number_calc_chisl = ?,
            #                     last_second_number_calc_znam = ?,
            #                     last_action_calc = ?
            #                     WHERE id = ?
            #                     """,
            #         elements,
            #     )
            # else:
            #     cursor.execute(
            #         f'INSERT INTO users VALUES({update.effective_user.id}, "{update.effective_user.username}", '
            #         f'"{result_action}",{result[0]}, {result[1]}, {result[2]}, "{first_num_action}", {first_num[0]},'
            #         f'{first_num[1]}, {first_num[2]}, "{second_num_action}", {second_num[0]}, {second_num[1]}, '
            #         f'{second_num[2]}, "{action}")')
            # conn.commit()

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