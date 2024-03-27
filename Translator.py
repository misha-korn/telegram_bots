import logging
import requests
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from config import config_2
from deep_translator import GoogleTranslator


#Настраиваем интерфейс логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
state = {}
languages = {'Английский': 'en', 'Немецкий': 'de', 'Русский': 'ru', 'Китайский': 'zh-CN'}

LANGUAGE_1, LANGUAGE_2, MESSAGE_TRANSLATE = range(1, 4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Английский', 'Немецкий', 'Русский', 'Китайский']]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="С какого языка вы бы хотели переводить?",
                                   reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=False))
    return LANGUAGE_1

async def first_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Английский', 'Немецкий', 'Русский', 'Китайский']]
    context.user_data['first_language'] = update.message.text
    if context.user_data['first_language'] == 'Английский':
        keyboard[0].pop(0)
    elif context.user_data['first_language'] == 'Немецкий':
        keyboard[0].pop(1)
    elif context.user_data['first_language'] == 'Русский':
        keyboard[0].pop(2)
    elif context.user_data['first_language'] == 'Китайский':
        keyboard[0].pop(3)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="На какой язык вы бы хотели переводить?",
                                   reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True))
    return LANGUAGE_2

async def second_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['second_language'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Какое сообщение вы бы хотели первести?")
    return MESSAGE_TRANSLATE

async def message_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['message'] = update.message.text
    context.user_data['new_message'] = GoogleTranslator(source=languages[context.user_data['first_language']],
                     target=languages[context.user_data['second_language']]).translate(context.user_data['message'])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=context.user_data['new_message'])
    return ConversationHandler.END




if __name__ == '__main__':
    application = ApplicationBuilder().token(config_2['token']).build()

    conv_hand = ConversationHandler(
                    entry_points=[CommandHandler('start', start)],
                    states={
                        LANGUAGE_1: [MessageHandler(filters.TEXT, first_language)],
                        LANGUAGE_2: [MessageHandler(filters.TEXT, second_language)],
                        MESSAGE_TRANSLATE: [MessageHandler(filters.TEXT, message_translate)]
                    },
                    fallbacks=[CommandHandler("start", start)]
    )
    application.add_handler(conv_hand)

    application.run_polling()