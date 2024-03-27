import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from config import config_3

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SCHEDULE, SIGN, SUBSCRIPTION, BUY = range(1, 5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            # первая строчка кнопочек
            InlineKeyboardButton('расписание', callback_data=str(SCHEDULE)),
            InlineKeyboardButton('запись', callback_data=str(SIGN)),
        ], [
            InlineKeyboardButton('абонемент', callback_data=str(SUBSCRIPTION)),
        ], [
            InlineKeyboardButton('купить', callback_data=str(BUY))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы попали на шахматный кружок!", reply_markup=reply_markup)


if __name__ == '__main__':
    application = ApplicationBuilder().token(config_3['token']).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()