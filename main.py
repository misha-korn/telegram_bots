import logging
import requests
import sqlite3
from telegram.constants import ParseMode
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# Настраиваем интерфейс логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
state = {}
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                                id INT PRIMARY KEY,
                                last_calc REAL);""")
conn.commit()


# Асинхронная функция, которая запускается по команде /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.args)
    if context.args and context.args[0] == "4orange":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Этот бот удалится через 15 секунд",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return
    keyboard = [["/calc", "dollar"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="[Яндекс](https://ya.ru)",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="[Йоу](https://t.me/test_korn_bot?start=4orange)",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )  # Выводит текст
    state[update.effective_user.id] = {"dia_stat": 0}
    print(state)


async def call_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query)
    await query.answer()
    valute_data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")

    keyboard_2 = [
        [
            # первая строчка кнопочек
            InlineKeyboardButton("USD", callback_data="USD"),
            InlineKeyboardButton("CNY", callback_data="CNY"),
            InlineKeyboardButton("AED", callback_data="AED"),
            InlineKeyboardButton("BYN", callback_data="BYN"),
        ]
    ]
    # lst = [[1]]
    # lst[0]
    if query.data == "CNY":
        keyboard_2[0].pop(1)
        await query.edit_message_text(
            valute_data.json()["Valute"]["CNY"]["Value"],
            reply_markup=InlineKeyboardMarkup(keyboard_2),
        )
    elif query.data == "USD":
        keyboard_2[0].pop(0)
        await query.edit_message_text(
            valute_data.json()["Valute"]["USD"]["Value"],
            reply_markup=InlineKeyboardMarkup(keyboard_2),
        )
    elif query.data == "AED":
        keyboard_2[0].pop(2)
        await query.edit_message_text(
            valute_data.json()["Valute"]["AED"]["Value"],
            reply_markup=InlineKeyboardMarkup(keyboard_2),
        )
    elif query.data == "BYN":
        keyboard_2[0].pop(3)
        await query.edit_message_text(
            valute_data.json()["Valute"]["BYN"]["Value"],
            reply_markup=InlineKeyboardMarkup(keyboard_2),
        )


async def dollar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["EUR", "CNY"], ["AED", "BYN"]]
    data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Курс доллара на сегодня {data.json()['Valute']['USD']['Value']}",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def EUR(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.to_json())
    keyboard = [
        [
            # первая строчка кнопочек
            InlineKeyboardButton("CNY", callback_data="CNY"),
            InlineKeyboardButton("AED", callback_data="AED"),
            InlineKeyboardButton("BYN", callback_data="BYN"),
        ]
    ]
    data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Курс евро на сегодня {data.json()['Valute']['EUR']['Value']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def CNY(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Курс китайских юань на сегодня {data.json()['Valute']['CNY']['Value']}",
    )


async def AED(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Курс Дирхам ОАЭ на сегодня {data.json()['Valute']['AED']['Value']}",
    )


async def BYN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Курс Белорусского рубля на сегодня {data.json()['Valute']['BYN']['Value']}",
    )


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state[update.effective_user.id]["dia_stat"] = 1
    print(state)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Введите первое число "
    )


async def message_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_message.text)
    if state[update.effective_user.id]["dia_stat"] == 1:
        state[update.effective_user.id]["first_num"] = int(
            update.effective_message.text
        )
        state[update.effective_user.id]["dia_stat"] = 2
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Введите второе число "
        )
    # elif 2 состояние, которое будет запоминать 2е число. 2е состояние переводит тебя на 3 и спрашивает действие
    # elif 3 состояние, сохраняет знак считает результат и печатает его. Откатываешься к 0 состоянию
    elif state[update.effective_user.id]["dia_stat"] == 2:
        state[update.effective_user.id]["second_num"] = int(
            update.effective_message.text
        )
        state[update.effective_user.id]["dia_stat"] = 3
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Введите знак "
        )
    elif state[update.effective_user.id]["dia_stat"] == 3:
        first_num = state[update.effective_user.id]["first_num"]
        second_num = state[update.effective_user.id]["second_num"]
        state[update.effective_user.id]["action"] = update.effective_message.text
        result = 0
        if state[update.effective_user.id]["action"] == "+":
            result = first_num + second_num
        elif state[update.effective_user.id]["action"] == "-":
            result = first_num - second_num
        elif state[update.effective_user.id]["action"] == "*":
            result = first_num * second_num
        elif state[update.effective_user.id]["action"] == "/":
            result = first_num / second_num
        await context.bot.send_message(chat_id=update.effective_chat.id, text=result)
        cursor.execute(
            f"SELECT id, last_calc FROM users WHERE id = {update.effective_user.id}"
        )
        # print(cursor.fetchone()) получаем кортеж с 2 числами или None
        data = cursor.fetchone()
        if data:
            cursor.execute(
                f"UPDATE users SET last_calc = {result} WHERE id = {update.effective_user.id}"
            )
        else:
            cursor.execute(
                f"INSERT INTO users VALUES({update.effective_user.id}, {result})"
            )
        conn.commit()
        state[update.effective_user.id]["dia_stat"] = 0

    if update.effective_message.text == "dollar":
        await dollar(update, context)

    if update.effective_message.text == "EUR":
        await EUR(update, context)

    if update.effective_message.text == "CNY":
        await CNY(update, context)

    if update.effective_message.text == "AED":
        await AED(update, context)

    if update.effective_message.text == "BYN":
        await BYN(update, context)

    # if context.args:
    #     text = int(context.args[0]) + int(context.args[1])
    # else:
    #     text = 'Ошибка вы не ввели вводные данные'
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.effective_user.username
    )


async def upper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        text = "Ошибка вы не ввели вводные данные"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    text = (" ".join(context.args)).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token("6658273201:AAHuwzqVF7EyHB1WdEp8RJSFMoJgyYHb3c4")
        .build()
    )

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    calc_handler = CommandHandler("calc", calc)  # Создаю обработчик команд
    application.add_handler(calc_handler)

    test_handler = CommandHandler("test", test)  # Создаю обработчик команд
    application.add_handler(test_handler)

    upper_handler = CommandHandler("upper", upper)
    application.add_handler(upper_handler)

    message_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), message_processing
    )
    application.add_handler(message_handler)

    call_back_handler = CallbackQueryHandler(call_back)
    application.add_handler(call_back_handler)

    application.run_polling()
