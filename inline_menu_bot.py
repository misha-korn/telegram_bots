import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler,
                          ConversationHandler, PreCheckoutQueryHandler, filters)
from config import config_3
from templates import keyboard_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

PAYMENT_PROVIDER_TOKEN = '381764678:TEST:82184'

SCHEDULE, SIGN, SUBSCRIPTION, BUY, CHOOSE_ACTION, PREVIOUS, NEXT, DAY, BUY_ONE_MONTH = range(1, 10)

day_of_week = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота', 7: 'Воскресенье'}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(keyboard_start)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы попали на шахматный кружок!",
                                   reply_markup=reply_markup)
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
    await query.edit_message_text('абонемент', reply_markup=reply_markup)
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
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_message.chat_id
    title = "Payment Example"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "RUB"
    # price in dollars
    price = 100
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Test", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    await update.message.reply_text("Thank you for your payment!")


if __name__ == '__main__':
    application = ApplicationBuilder().token(config_3['token']).build()

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
                CallbackQueryHandler(start_without_shipping_callback, pattern=f'^{BUY_ONE_MONTH}$'),
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
