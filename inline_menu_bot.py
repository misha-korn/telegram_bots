import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler,
                          ConversationHandler)
from config import config_3
from templates import keyboard_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SCHEDULE, SIGN, SUBSCRIPTION, BUY, CHOOSE_ACTION, PREVIOUS, NEXT, DAY = range(1, 9)


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
            InlineKeyboardButton('главное меню', callback_data=str(CHOOSE_ACTION)),
        ], [
            InlineKeyboardButton('запись', callback_data=str(SIGN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    if query.data == str(SCHEDULE):
        await query.edit_message_text('расписание', reply_markup=reply_markup)


async def subscription_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton('главное меню', callback_data=str(CHOOSE_ACTION)),
        ], [
            InlineKeyboardButton('запись', callback_data=str(SIGN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    if query.data == str(SCHEDULE):
        await query.edit_message_text('расписание', reply_markup=reply_markup)


async def buy_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton('главное меню', callback_data=str(CHOOSE_ACTION)),
        ], [
            InlineKeyboardButton('запись', callback_data=str(SIGN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    if query.data == str(SCHEDULE):
        await query.edit_message_text('расписание', reply_markup=reply_markup)


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
            ]
        },
        fallbacks=[]
    )

    application.add_handler(conv_hand)

    application.run_polling()
