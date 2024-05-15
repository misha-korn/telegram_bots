import logging
import sqlite3
import json
import datetime
import pytz
from calendar import monthrange
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from config import config_5

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

state = {}
dict_bd_name = {}
dict_bd_rep = {}

conn = sqlite3.connect('+rep_bot_db.sqlite')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                                    id INT PRIMARY KEY,
                                    name TEXT);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS reputation(
                                    id INT PRIMARY KEY,
                                    reputation INT);''')

# for i in range(8):
#     name = f'gleb{i}'
#
#     cursor.execute(
#             f'INSERT INTO users VALUES({87654321+i}, "{name}")'
#         )
#     cursor.execute(
#         f'INSERT INTO reputation VALUES({87654321+i}, {0})'
#     )
# conn.commit()
#
# name = 'vasia'
#
# cursor.execute(
#         f'INSERT INTO users VALUES({34567890}, "{name}")'
#     )
# cursor.execute(
#     f'INSERT INTO reputation VALUES({34567890}, {0})'
# )
#
# name = 'petia'
#
# cursor.execute(
#         f'INSERT INTO users VALUES({67890543}, "{name}")'
#     )
# cursor.execute(
#     f'INSERT INTO reputation VALUES({67890543}, {0})'
# )
# conn.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('+rep_bot_db.sqlite')
    cursor = conn.cursor()
    user_list = cursor.execute(f'SELECT id FROM users WHERE id = "{update.effective_user.id}"').fetchone()
    # print(user_list[0]==True)
    # print(user_list)
    if user_list == None:
        # print(update.effective_user.id, update.effective_user.username)
        cursor.execute(
            f'INSERT INTO users VALUES({update.effective_user.id}, "{update.effective_user.username}")'
        )
        cursor.execute(
            f'INSERT INTO reputation VALUES({update.effective_user.id}, {0})'
        )
        conn.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы успешно зарегистрировались!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Приветствуем вас, "
                                                                              f"{update.effective_user.username}!")

    context.job_queue.run_daily(
        write_rep,
        time=datetime.time(hour=18, minute=36, tzinfo=pytz.timezone("Europe/Moscow")),
        chat_id=update.effective_chat.id,
    )

async def write_rep(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    conn = sqlite3.connect('+rep_bot_db.sqlite')
    cursor = conn.cursor()
    text = 'Репутация участников:'
    user_id_all = cursor.execute(f'SELECT id FROM users').fetchall()
    # print(user_id_all)
    for user_id_one in user_id_all:
        dict_bd_name[user_id_one[0]] = cursor.execute(f'SELECT name FROM users WHERE id = {user_id_one[0]}').fetchone()[0]
        dict_bd_rep[user_id_one[0]] = cursor.execute(f'SELECT reputation FROM reputation WHERE id = {user_id_one[0]}').fetchone()[0]
    # print(dict_bd_name)
    # print(dict_bd_rep)
    for user_id_one in user_id_all:
        text = f'{text}\n • {dict_bd_name[user_id_one[0]]} - {dict_bd_rep[user_id_one[0]]}.'
    await context.bot.send_message(chat_id=job.chat_id, text=text)

async def rep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('+rep_bot_db.sqlite')
    cursor = conn.cursor()
    user_names = cursor.execute(f'SELECT name FROM users WHERE id != "{update.effective_user.id}"').fetchall()
    user_names_new = []
    for element in user_names:
        user_names_new.append(element[0])
    state['user_names_new_rep'] = user_names_new
    state['user_names_rep'] = user_names
    len_string = 3
    keyboard = [[] for i in range(len(user_names)//len_string+1)]
    i = 0
    for user_name in state['user_names_rep']:
        keyboard[i//len_string].append(InlineKeyboardButton(str(user_name[0]), callback_data=str(user_name[0])))
        i += 1

    # print(keyboard)

    len_keyboard = 0
    for lst in keyboard:
        len_keyboard += len(lst)

    if len_keyboard == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="К сожалению, вы не можете никому "
                                                                              "повысить репутацию, т.к вы находитесь "
                                                                              "одни в этом чате")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Кому бы вы хотели повысить репутацию?",
                                       reply_markup=InlineKeyboardMarkup(keyboard))

async def call_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    conn = sqlite3.connect('+rep_bot_db.sqlite')
    cursor = conn.cursor()
    await query.answer()
    if query.data in state['user_names_new_rep'] and str(query.data) != update.effective_user.username:
        id_rep = cursor.execute(f'SELECT id FROM users WHERE name = "{query.data}"').fetchone()[0]
        rep = cursor.execute(f'SELECT reputation FROM reputation WHERE id = "{id_rep}"').fetchone()[0]
        cursor.execute(
            f'UPDATE reputation SET reputation = {rep + 1} WHERE id = {id_rep}'
        )
        conn.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Репутация {query.data} повышена!\nТ'
                                                                              f'еперь репутация {query.data} равна '
                                                                              f'{rep + 1}')
    elif str(query.data) == update.effective_user.username:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Вы не можете повысить репутацию самому себе')

if __name__ == '__main__':
    application = ApplicationBuilder().token(config_5['token']).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    rep_handler = CommandHandler('plus_rep', rep)
    application.add_handler(rep_handler)

    call_back_handler = CallbackQueryHandler(call_back)
    application.add_handler(call_back_handler)

    application.run_polling()