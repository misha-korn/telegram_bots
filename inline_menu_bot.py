import logging
import sqlite3
import pytz
from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    PreCheckoutQueryHandler,
    filters,
)
from database import create_bd

from config import config_6
from templates import keyboard_start
import json
import datetime
from calendar import monthrange

# Enable logging
logging.basicConfig(
    # filename="chess_log.txt",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

state = {}
state["sign_for_lesson"] = 0

PAYMENT_PROVIDER_TOKEN = "381764678:TEST:86788"

(
    BUY_ONE_WEEK,
    BUY_ONE_MONTH,
    BUY_ONE_YEAR,
    SCHEDULE,
    SIGN,
    SUBSCRIPTION,
    BUY,
    CHOOSE_ACTION,
    PREVIOUS,
    NEXT,
    DAY,
) = range(0, 11)

day_of_week = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.args)
    # created_8_lessons()
    if context.args:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
        )
        id_les = int(context.args[0].split("_")[-1])
        await sign(update, id_les, context)
        if context.args[0][0] == "h":
            return SCHEDULE
        else:
            return SIGN
    else:
        with sqlite3.connect("inline_menu_bot_db.sqlite3") as conn:
            cursor = conn.cursor()
            user_list = cursor.execute(
                f"SELECT id FROM users WHERE id = {update.effective_user.id}"
            )
            if not user_list.fetchone():
                cursor.execute(
                    f'INSERT INTO users VALUES({update.effective_user.id}, "{update.effective_user.username}")'
                )
                conn.commit()
        reply_markup = InlineKeyboardMarkup(keyboard_start)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы попали на шахматный кружок!",
            reply_markup=reply_markup,
        )
        return CHOOSE_ACTION


async def sign(update: Update, id_les, context):
    with sqlite3.connect("inline_menu_bot_db.sqlite3") as conn:
        cursor = conn.cursor()
        abonement_list = cursor.execute(
            f"SELECT id, visit_lessons, count_lessons FROM abonements WHERE user_id = {update.effective_user.id} and status = 1"
        ).fetchall()
        status = 1
        try:
            ab_visit_lesson = abonement_list[0][1] + 1
        except IndexError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Вы не можете записаться на урок, не купив абонемент!",
            )
            return
        if ab_visit_lesson == abonement_list[0][2]:
            status = 0
        cursor.execute(
            f"UPDATE abonements SET visit_lessons = {ab_visit_lesson}, status={status} WHERE id={abonement_list[0][0]}"
        )
        cursor.execute(
            f"INSERT INTO lessons_info VALUES({abonement_list[0][0]}, {id_les})"
        )
        conn.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Вы успешно записались на урок!"
        )


async def hello(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id, text=f"Привет {job.data['name']}"
    )


async def printing(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id, text="Запишись на урок, если ещё не записался"
    )


async def chooseact_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(keyboard_start)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Вы попали на шахматный кружок!", reply_markup=reply_markup
    )
    return CHOOSE_ACTION


async def change_page_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == str(PREVIOUS):
        if context.user_data["num_day"] > 1:
            context.user_data["num_day"] -= 1
    elif query.data == str(NEXT):
        if context.user_data["num_day"] < 7:
            context.user_data["num_day"] += 1
    else:
        return SCHEDULE
    await schedule_cb(update, context)
    return SCHEDULE


async def schedule_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("inline_menu_bot_db.sqlite3")
    cursor = conn.cursor()
    text = "расписание"
    if not context.user_data.get("num_day"):
        context.user_data["num_day"] = 1
    today_d = datetime.date.today()
    td = datetime.timedelta(days=7)
    next_week_d = today_d + td
    today_d = today_d.strftime("%Y-%m-%d")
    next_week_d = next_week_d.strftime("%Y-%m-%d")
    lessons_week = cursor.execute(
        f'SELECT date_lessons, id FROM lessons WHERE date_lessons >= "{today_d}" and date_lessons <= "{next_week_d}"'
    ).fetchall()
    for lesson in lessons_week:
        num_day = datetime.datetime.strptime(lesson[0], "%Y-%m-%d").date().weekday()
        if num_day == context.user_data["num_day"] - 1:
            text = f"[{lesson[0]}](https://t.me/inline_chess_bot?start=hsign_les_{lesson[1]})"
            break
        else:
            text = "На выбранную дату не найдены уроки."
    keyboard = [
        [
            InlineKeyboardButton("◀️", callback_data=str(PREVIOUS)),
            InlineKeyboardButton(
                f'{context.user_data["num_day"]}/7', callback_data=str(DAY)
            ),
            InlineKeyboardButton("▶️", callback_data=str(NEXT)),
        ],
        [
            InlineKeyboardButton(
                day_of_week[context.user_data["num_day"]], callback_data=str(DAY)
            ),
        ],
        [
            InlineKeyboardButton("главное меню", callback_data=str(CHOOSE_ACTION)),
        ],
        [
            InlineKeyboardButton("запись", callback_data=str(SIGN)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    # print(context.user_data['num_day'], query.data)
    await query.answer()
    text = text.replace(".", "\.")
    text = text.replace("-", "\-")
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2
    )
    return SCHEDULE


async def sign_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("расписание", callback_data=str(SCHEDULE)),
        ],
        [
            InlineKeyboardButton("главное меню", callback_data=str(CHOOSE_ACTION)),
        ],
        [
            InlineKeyboardButton("абонемент", callback_data=str(SUBSCRIPTION)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()

    text_sign = "Доступные записи на уроки:"

    conn = sqlite3.connect("inline_menu_bot_db.sqlite3")
    cursor = conn.cursor()
    today_d = datetime.date.today()
    month_days = monthrange(today_d.year, today_d.month)
    td = datetime.timedelta(days=month_days[1])
    next_month_d = today_d + td
    today_d = today_d.strftime("%Y-%m-%d")  # '2024-05-12'
    next_month_d = next_month_d.strftime("%Y-%m-%d")
    data_lessons = cursor.execute(
        f'SELECT id, date_lessons FROM lessons WHERE date_lessons >= "{today_d}" and date_lessons <= "{next_month_d}"'
    ).fetchall()
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text="[Йоу](https://t.me/test_korn_bot?start=4orange)",
    #     parse_mode=ParseMode.MARKDOWN_V2,
    # )
    for n, lesson in enumerate(data_lessons):
        text_sign = f"{text_sign}\n{n+1}. [{lesson[1]}](https://t.me/inline_chess_bot?start=sign_les_{lesson[0]})."
    text_sign = text_sign.replace(".", "\.")
    text_sign = text_sign.replace("-", "\-")
    if len(data_lessons) == 0:
        text_subscription = "У вас нет доступных уроков для записи"
    await query.edit_message_text(
        text_sign,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return SIGN


async def subscription_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("расписание", callback_data=str(SCHEDULE)),
        ],
        [
            InlineKeyboardButton("главное меню", callback_data=str(CHOOSE_ACTION)),
        ],
        [
            InlineKeyboardButton("запись", callback_data=str(SIGN)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    text_subscription = "Ваши абонементы:"

    conn = sqlite3.connect("inline_menu_bot_db.sqlite3")
    cursor = conn.cursor()
    abonements = cursor.execute(
        f'SELECT count_lessons FROM abonements WHERE user_id = "{update.effective_user.id}"'
    ).fetchall()
    payments = cursor.execute(
        f'SELECT sum FROM payments WHERE user_id = "{update.effective_user.id}"'
    ).fetchall()
    count_visit_lessons = cursor.execute(
        f'SELECT visit_lessons FROM abonements WHERE user_id = "{update.effective_user.id}"'
    ).fetchall()
    if count_visit_lessons:
        count_visit_lessons = count_visit_lessons[0][0]
    else:
        count_visit_lessons = 0
    count_visit_lessons_copy = count_visit_lessons
    print(count_visit_lessons)
    visit_lessons_counter = 0
    for i in range(len(abonements)):
        text_subscription = f"{text_subscription}\n{i+1}. {int(abonements[i][0])} уроков, стоимостью {int(payments[i][0]/100)} рублей."
        if count_visit_lessons_copy >= int(abonements[i][0]):
            text_subscription = f"{text_subscription[:-1]} - не действителен."
            count_visit_lessons_copy -= int(abonements[i][0])
        else:
            text_subscription = f"{text_subscription[:-1]} - действителен."
        visit_lessons_counter += int(abonements[i][0])
    text_subscription = f"{text_subscription[:-1]}\nУ вас осталось {visit_lessons_counter-count_visit_lessons} абонементов."

    if len(abonements) == 0:
        text_subscription = "У вас нет абонементов"

    await query.edit_message_text(text_subscription, reply_markup=reply_markup)
    return SUBSCRIPTION


async def buy_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("расписание", callback_data=str(SCHEDULE)),
        ],
        [
            InlineKeyboardButton("главное меню", callback_data=str(CHOOSE_ACTION)),
        ],
        [
            InlineKeyboardButton("запись", callback_data=str(SIGN)),
        ],
        [
            InlineKeyboardButton(
                "купить абонемент на месяц", callback_data=str(BUY_ONE_MONTH)
            ),
        ],
        [
            InlineKeyboardButton(
                "купить абонемент на неделю", callback_data=str(BUY_ONE_WEEK)
            ),
        ],
        [
            InlineKeyboardButton(
                "купить абонемент на год", callback_data=str(BUY_ONE_YEAR)
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("купить", reply_markup=reply_markup)
    return BUY


async def start_without_shipping_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends an invoice without shipping-payment."""
    with open("payment_details.json") as file:
        payment_info = json.loads(file.read())
    print(payment_info)
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_message.chat_id
    # if query.data ==
    title = payment_info[int(query.data)]["title"]
    description = payment_info[int(query.data)]["description"]
    payload = f"{payment_info[int(query.data)]['number_lessons']}"
    currency = "RUB"
    price = payment_info[int(query.data)]["price"]
    prices = [LabeledPrice("Test", price * 100)]
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices
    )


async def precheckout_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload not in ["2", "8", "72"]:
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    print(update)
    await update.message.reply_text("Спасибо за покупку!")
    with sqlite3.connect("inline_menu_bot_db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO payments VALUES(NULL, {update.effective_user.id}, {update.effective_message.successful_payment.total_amount})"
        )
        pay_id = cursor.execute(
            f'SELECT seq FROM sqlite_sequence WHERE name="payments"'
        ).fetchone()[0]
        number_lessons = int(
            update.effective_message.successful_payment.invoice_payload
        )
        cursor.execute(
            f"INSERT INTO abonements (user_id, pay_id, count_lessons) VALUES({update.effective_user.id}, {pay_id}, {number_lessons})"
        )
        conn.commit()


def created_2_lessons(context) -> None:
    conn = sqlite3.connect("inline_menu_bot_db.sqlite3")
    cursor = conn.cursor()

    td = datetime.timedelta(days=2)
    today = datetime.date.today()
    # 2024-05-20
    # 2024-05-22
    # if state["sign_for_lesson"] == 0:
    for i in range(2):
        today += td
        cursor.execute(
            f'INSERT INTO lessons VALUES(NULL, "{today.strftime("%Y-%m-%d")}") '
        )
    conn.commit()
    conn.close()
    # state["sign_for_lesson"] += 1
    # if state["sign_for_lesson"] > 3:
    #     state["sign_for_lesson"] = 0


def created_8_lessons() -> None:
    conn = sqlite3.connect("inline_menu_bot_db.sqlite3")
    cursor = conn.cursor()
    # 2024-05-20
    # 2024-05-22
    for i in range(8):
        cursor.execute(f'INSERT INTO lessons VALUES(NULL, "2024-06-{1+(i*2)}") ')
    conn.commit()


if __name__ == "__main__":
    application = ApplicationBuilder().token(config_6["token"]).build()
    create_bd("inline_menu_bot_db.sqlite3")
    # created_8_lessons()
    conv_hand = ConversationHandler(
        entry_points=[CommandHandler("start", start, has_args=False)],
        states={
            CHOOSE_ACTION: [
                CallbackQueryHandler(schedule_cb, pattern=f"^{SCHEDULE}$"),
                CallbackQueryHandler(sign_cb, pattern=f"^{SIGN}$"),
                CallbackQueryHandler(subscription_cb, pattern=f"^{SUBSCRIPTION}$"),
                CallbackQueryHandler(buy_cb, pattern=f"^{BUY}$"),
            ],
            SCHEDULE: [
                CommandHandler("start", start, has_args=True),
                CallbackQueryHandler(
                    change_page_cb, pattern=f"^({NEXT}|{PREVIOUS}|{DAY})$"
                ),
                CallbackQueryHandler(sign_cb, pattern=f"^{SIGN}$"),
                CallbackQueryHandler(chooseact_cb, pattern=f"^{CHOOSE_ACTION}$"),
            ],
            SUBSCRIPTION: [
                CallbackQueryHandler(schedule_cb, pattern=f"^{SCHEDULE}$"),
                CallbackQueryHandler(sign_cb, pattern=f"^{SIGN}$"),
                CallbackQueryHandler(chooseact_cb, pattern=f"^{CHOOSE_ACTION}$"),
            ],
            SIGN: [
                CommandHandler("start", start, has_args=True),
                CallbackQueryHandler(schedule_cb, pattern=f"^{SCHEDULE}$"),
                CallbackQueryHandler(subscription_cb, pattern=f"^{SUBSCRIPTION}$"),
                CallbackQueryHandler(chooseact_cb, pattern=f"^{CHOOSE_ACTION}$"),
            ],
            BUY: [
                CallbackQueryHandler(schedule_cb, pattern=f"^{SCHEDULE}$"),
                CallbackQueryHandler(sign_cb, pattern=f"^{SIGN}$"),
                CallbackQueryHandler(chooseact_cb, pattern=f"^{CHOOSE_ACTION}$"),
                CallbackQueryHandler(
                    start_without_shipping_callback,
                    pattern=f"^({BUY_ONE_MONTH}|"
                    f"{BUY_ONE_WEEK}|"
                    f"{BUY_ONE_YEAR})$",
                ),
            ],
        },
        fallbacks=[CommandHandler("start", start, has_args=False)],
    )

    application.add_handler(conv_hand)

    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    conn = sqlite3.connect("inline_menu_bot_db.sqlite3")
    cursor = conn.cursor()
    if len(cursor.execute(f"SELECT * FROM lessons").fetchall()) == 0:
        created_2_lessons(4)
        conn.commit()
    conn.close()

    application.job_queue.run_repeating(
        created_2_lessons,
        interval=datetime.timedelta(days=4),
        #     first=datetime.time(hour=12, minute=00, tzinfo=pytz.timezone("Europe/Moscow")),
        first=datetime.timedelta(days=4),
    )

    application.run_polling()
