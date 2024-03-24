import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

#Настраиваем интерфейс логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
state = {}

# def sokrashenie(result_1, result_2, s):
#     print('я запустился')
#     for i in range(2, int(result_1) // 2 + 1):
#         print('делаю проверку')
#         if result_2 % i == 0 and result_1 % i == 0:
#             result_2 /= i
#             result_1 /= i
#             s += 2
#             print(result_1, result_2, i)
#     s -= 1
#     return result_1, result_2, s


def sokrashenie(result_1, result_2, s):
    print('я запустил функцию')
    i = 2
    while i <= (int(result_1) // 2):
        print('делаю проверку номер ', i - 1, ' конечное число ', int(result_1) // 2 - 1)
        if result_2 % i == 0 and result_1 % i == 0:
            result_2 /= i
            result_1 /= i
            s += 2
            print(result_1, result_2, i)
        i += 1
    s -= 1
    return result_1, result_2, s

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['/nod', '/nok', '/calc']]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите действие", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))#Выводит текст
    state[update.effective_user.id] = {'dia_stat': 0}


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]['dia_stat'] = 1
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите первое число, если число дробное, то дробную часть отделите от целой пробелом, при её записи используте /. Вот пример записи 5 5/6 или 0 2/7")

async def nod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]['dia_stat'] = 'nod_1'
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите 2 целых числа, чтобы я сказал вам их НОД")

async def nok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]['dia_stat'] = 'nok_1'
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите 2 целых числа, чтобы я сказал вам их НОК")

async def message_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print(lst)
        if len(lst) == 2:
            drob = lst[1].split('/')
            chisl_1 = int(drob[0])
            znamen_1 = int(drob[1])
            state[update.effective_user.id]['first_num'] = [cel_1, chisl_1, znamen_1]
            # state[update.effective_user.id]['first_num'] = int(lst[0]) + int(drob[0]) * (1/int(drob[1]))
        if len(lst) == 1 or (len(lst) == 2 and int(lst[1].split('/')[1]) == 0):
            state[update.effective_user.id]['first_num'] = [cel_1, 0, 1]
        print(update.effective_message.text)
        state[update.effective_user.id]['dia_stat'] = 2
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите второе число ")

    elif state[update.effective_user.id]['dia_stat'] == 2:
        lst_2 = update.effective_message.text.split(' ')
        cel_2 = int(lst_2[0])
        print(lst_2)
        if len(lst_2) == 2:
            drob = lst_2[1].split('/')
            chisl_2 = int(drob[0])
            znamen_2 = int(drob[1])
            state[update.effective_user.id]['second_num'] = [cel_2, chisl_2, znamen_2]
            # state[update.effective_user.id]['second_num'] = int(lst[0]) + int(drob[0]) * (1 / int(drob[1]))
        if len(lst_2) == 1 or (len(lst_2) == 2 and int(lst_2[1].split('/')[1]) == 0):
            state[update.effective_user.id]['second_num'] = [cel_2, 0, 1]
        print(update.effective_message.text)
        state[update.effective_user.id]['dia_stat'] = 3
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите знак ")

    elif state[update.effective_user.id]['dia_stat'] == 3:
        first_num = state[update.effective_user.id]['first_num']
        second_num = state[update.effective_user.id]['second_num']
        state[update.effective_user.id]['action'] = update.effective_message.text
        if first_num[0] >= 1000000000000000000000000000 or second_num[0] >= 1000000000000000000000000000:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Введите 2 числа поменьше, чтобы не нагружать сервер')
            await calc(update, context)
        else:
            print(state[update.effective_user.id]['action'])
            print(first_num, second_num)
            result = 0
            if state[update.effective_user.id]['action'] == '+':
                result = [first_num[0] + second_num[0],
                          first_num[1] * second_num[2] + second_num[1] * first_num[2],
                          first_num[2] * second_num[2]]
                if result[1] >= result[2]:
                    result[0] += result[1] // result[2]
                    result[1] -= result[2] * (result[1] // result[2])

            elif state[update.effective_user.id]['action'] == '-':
                result = [first_num[0] - second_num[0],
                          first_num[1] * second_num[2] - second_num[1] * first_num[2],
                          first_num[2] * second_num[2]]
                if result[1] < 0:
                    result[0] -= (-result[1] // result[2]) + 1
                    result[1] += result[2]

            elif state[update.effective_user.id]['action'] == '*':
                result = [0,
                          (first_num[1]+first_num[0]*first_num[2])*(second_num[1]+second_num[0]*second_num[2]),
                          first_num[2] * second_num[2]]
                if result[1] >= result[2]:
                    result[0] += result[1] // result[2]
                    result[1] -= result[2] * (result[1] // result[2])

            elif state[update.effective_user.id]['action'] in ['/', ':']:
                result = [0,
                          (first_num[1]+first_num[0]*first_num[2])*(second_num[2]),
                          (first_num[2]) * (second_num[1]+second_num[0]*second_num[2])]
                if result[1] >= result[2]:
                    result[0] += result[1] // result[2]
                    result[1] -= result[2] * (result[1] // result[2])
                print(result)
            if int(result[1]) // 2 >= 5000000:
                text = f'Мы не можем сократить полученый нами результат, ' \
                       f'т.к числитель или знаменатель вводных чисел слишком большой.' \
                       f'Однако мы можем сказать вам не сокращенную дробь. {result[0]} {result[1]}/{result[2]}'
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=text)
            else:
                s = 1
                sokr = sokrashenie(result[1], result[2], s)
                result[1] = sokr[0]
                result[2] = sokr[1]
                s = sokr[2]
                while s > 1:
                    sokr = sokrashenie(result[1], result[2], s)
                    result[1] = sokr[0]
                    result[2] = sokr[1]
                    s = sokr[2]
                if int(sokr[0]) == 0 and int(sokr[1]) == 1:
                    text = f'{int(result[0])}'
                else:
                    text = f'{int(result[0])} {int(sokr[0])}/{int(sokr[1])}'
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

if __name__ == '__main__':
    application = ApplicationBuilder().token('6995737865:AAFhAW8qSc7js31vm_lzAvAVd-DeK1ZsZ5E').build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    calc_handler = CommandHandler('calc', calc)  # Создаю обработчик команд
    application.add_handler(calc_handler)

    nod_handler = CommandHandler('nod', nod)
    application.add_handler(nod_handler)

    nok_handler = CommandHandler('nok', nok)
    application.add_handler(nok_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_processing)
    application.add_handler(message_handler)

    application.run_polling()