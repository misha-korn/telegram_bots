import logging
import sqlite3

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler,
                          ConversationHandler, PreCheckoutQueryHandler, filters)
from database import create_bd

from config import config_3
from templates import keyboard_start
import json

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

PAYMENT_PROVIDER_TOKEN = '381764678:TEST:82184'

BUY_ONE_WEEK, BUY_ONE_MONTH, BUY_ONE_YEAR, SCHEDULE, SIGN, SUBSCRIPTION, BUY, CHOOSE_ACTION, PREVIOUS, NEXT, DAY = (
    range(0, 11))

day_of_week = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота', 7: 'Воскресенье'}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(keyboard_start)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы попали на шахматный кружок!",
                                   reply_markup=reply_markup)

    with sqlite3.connect('inline_menu_bot_db.sqlite3') as conn:
        cursor = conn.cursor()
        user_list = cursor.execute(
            f'SELECT id FROM users WHERE id = {update.effective_user.id}')
        if not user_list.fetchone():
            cursor.execute(
                f'INSERT INTO users VALUES({update.effective_user.id}, "{update.effective_user.username}")')
            conn.commit()
    return CHOOSE_ACTION


async def chooseact_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(keyboard_start)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Вы попали на шахматный кружок!", reply_markup=reply_markup)
    return CHOOSE_ACTION


async def change_page_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == str(PREVIOUS):
        if context.user_data['num_day'] > 1:
            context.user_data['num_day'] -= 1
    elif query.data == str(NEXT):
        if context.user_data['num_day'] < 7:
            context.user_data['num_day'] += 1
    else:
        return SCHEDULE
    await schedule_cb(update, context)
    return SCHEDULE


async def schedule_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('num_day'):
        context.user_data['num_day'] = 1

    keyboard = [[
                    InlineKeyboardButton('◀️', callback_data=str(PREVIOUS)),
                    InlineKeyboardButton(f'{context.user_data["num_day"]}/7', callback_data=str(DAY)),
                    InlineKeyboardButton('▶️', callback_data=str(NEXT)),
                ], [
                    InlineKeyboardButton(day_of_week[context.user_data["num_day"]], callback_data=str(DAY)),
                ], [
                    InlineKeyboardButton('главное меню', callback_data=str(CHOOSE_ACTION)),
                ], [
                    InlineKeyboardButton('запись', callback_data=str(SIGN)),
                ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    # print(context.user_data['num_day'], query.data)
    await query.answer()
    await query.edit_message_text('расписание', reply_markup=reply_markup)
    return SCHEDULE


async def sign_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton('расписание', callback_data=str(SCHEDULE)),
        ], [
            InlineKeyboardButton('главное меню', callback_data=str(CHOOSE_ACTION)),
        ], [
            InlineKeyboardButton('абонемент', callback_data=str(SUBSCRIPTION)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text('запись', reply_markup=reply_markup)
    return SIGN


async def subscription_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton('расписание', callback_data=str(SCHEDULE)),
        ], [
            InlineKeyboardButton('главное меню', callback_data=str(CHOOSE_ACTION)),
        ], [
            InlineKeyboardButton('запись', callback_data=str(SIGN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    text_subscription = 'Ваши абонементы:'

    conn = sqlite3.connect('inline_menu_bot_db.sqlite3')
    cursor = conn.cursor()
    abonements = cursor.execute(f'SELECT count_lessons FROM abonements WHERE user_id = "{update.effective_user.id}"').fetchall()
    payments = cursor.execute(f'SELECT sum FROM payments WHERE user_id = "{update.effective_user.id}"').fetchall()
    
    for i in range(len(abonements)):
        text_subscription = f'{text_subscription}\n{i+1}. {int(abonements[i][0])} уроков, стоимостью {int(payments[i][0]/100)} рублей.'
    
    if len(abonements) == 0:
        text_subscription = 'У вас нет абонементов'

    await query.edit_message_text(text_subscription, reply_markup=reply_markup)
    return SUBSCRIPTION


async def buy_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton('расписание', callback_data=str(SCHEDULE)),
        ], [
            InlineKeyboardButton('главное меню', callback_data=str(CHOOSE_ACTION)),
        ], [
            InlineKeyboardButton('запись', callback_data=str(SIGN)),
        ], [
            InlineKeyboardButton('купить абонемент на месяц', callback_data=str(BUY_ONE_MONTH)),
        ], [
            InlineKeyboardButton('купить абонемент на неделю', callback_data=str(BUY_ONE_WEEK)),
        ], [
            InlineKeyboardButton('купить абонемент на год', callback_data=str(BUY_ONE_YEAR)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text('купить', reply_markup=reply_markup)
    return BUY

async def start_without_shipping_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends an invoice without shipping-payment."""
    with open('payment_details.json') as file:
        payment_info = json.loads(file.read())
    print(payment_info)
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_message.chat_id
    # if query.data ==
    title = payment_info[int(query.data)]['title']
    description = payment_info[int(query.data)]['description']
    payload = f"{payment_info[int(query.data)]['number_lessons']}"
    currency = "RUB"
    price = payment_info[int(query.data)]['price']
    prices = [LabeledPrice("Test", price * 100)]
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload not in ['2','8','72']:
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    print(update)
    await update.message.reply_text("Спасибо за покупку!")
    with sqlite3.connect('inline_menu_bot_db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO payments VALUES(NULL, {update.effective_user.id}, {update.effective_message.successful_payment.total_amount})')
        pay_id = cursor.execute(f'SELECT seq FROM sqlite_sequence WHERE name="payments"').fetchone()[0]
        number_lessons = int(update.effective_message.successful_payment.invoice_payload)
        cursor.execute(f'INSERT INTO abonements VALUES(NULL, {update.effective_user.id}, {pay_id}, {number_lessons})')
        conn.commit()

def created_8_lessons() -> None:
    conn = sqlite3.connect('inline_menu_bot_db.sqlite3')
    cursor = conn.cursor()
    #2024-05-20
    #2024-05-22
    for i in range(8):
        cursor.execute(f'INSERT INTO lessons VALUES(NULL, "2024-05-{20+(i*2)}") ')
    conn.commit()



if __name__ == '__main__':
    application = ApplicationBuilder().token(config_3['token']).build()
    create_bd('inline_menu_bot_db.sqlite3')
    # created_8_lessons()
    conv_hand = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_ACTION: [
                CallbackQueryHandler(schedule_cb, pattern=f'^{SCHEDULE}$'),
                CallbackQueryHandler(sign_cb, pattern=f'^{SIGN}$'),
                CallbackQueryHandler(subscription_cb, pattern=f'^{SUBSCRIPTION}$'),
                CallbackQueryHandler(buy_cb, pattern=f'^{BUY}$'),
            ],
            SCHEDULE: [
                CallbackQueryHandler(change_page_cb, pattern=f'^({NEXT}|{PREVIOUS}|{DAY})$'),
                CallbackQueryHandler(sign_cb, pattern=f'^{SIGN}$'),
                CallbackQueryHandler(chooseact_cb, pattern=f'^{CHOOSE_ACTION}$'),
            ],
            SUBSCRIPTION: [
                CallbackQueryHandler(schedule_cb, pattern=f'^{SCHEDULE}$'),
                CallbackQueryHandler(sign_cb, pattern=f'^{SIGN}$'),
                CallbackQueryHandler(chooseact_cb, pattern=f'^{CHOOSE_ACTION}$'),
            ],
            SIGN: [
                CallbackQueryHandler(schedule_cb, pattern=f'^{SCHEDULE}$'),
                CallbackQueryHandler(subscription_cb, pattern=f'^{SUBSCRIPTION}$'),
                CallbackQueryHandler(chooseact_cb, pattern=f'^{CHOOSE_ACTION}$'),
            ],
            BUY: [
                CallbackQueryHandler(schedule_cb, pattern=f'^{SCHEDULE}$'),
                CallbackQueryHandler(sign_cb, pattern=f'^{SIGN}$'),
                CallbackQueryHandler(chooseact_cb, pattern=f'^{CHOOSE_ACTION}$'),
                CallbackQueryHandler(start_without_shipping_callback, pattern=f'^({BUY_ONE_MONTH}|'
                                                                              f'{BUY_ONE_WEEK}|'
                                                                              f'{BUY_ONE_YEAR})$'),
            ]
        },
        fallbacks=[]
    )

    application.add_handler(conv_hand)

    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    application.run_polling()
