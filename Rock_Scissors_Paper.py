import logging
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

#Настраиваем интерфейс логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
state = {}
rules = '''Игроки вместе считают вслух: «Камень… Ножницы… Бумага… Раз… Два… Три», __одновременно качая кулаками__.
На счёт «Три» они одновременно показывают при помощи руки один из трёх знаков: камень, ножницы или бумагу.
Победитель определяется по следующим правиламБумага побеждает камень («бумага обёртывает камень»).
Камень побеждает ножницы («камень затупляет ножницы»).Ножницы побеждают бумагу («ножницы разрезают бумагу»). 
**Сыграем еще раз?**'''

# Асинхронная функция, которая запускается по команде /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Давай', 'Не хочу', '/help']]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Сыграем в игру?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))
    state[update.effective_user.id] = {'dia_stat': 0}

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Давай', 'Не хочу']]
    await context.bot.send_message(chat_id=update.effective_chat.id, text= rules, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))
    state[update.effective_user.id] = {'dia_stat': 0}

async def message_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Давай']]
    if update.effective_message.text == 'Не хочу':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Хорошо. Если, вдруг, захочешь сыграть - напиши Давай!', reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))
    if update.effective_message.text == 'Давай':
        keyboard = [['Камень', 'Ножницы', 'Бумага', '/help']]
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Отлично! Делай свой выбор!', reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))

    if update.effective_message.text == 'Камень':
        answer = ''
        keyboard = [
            [
                # первая строчка кнопочек
                InlineKeyboardButton('Давай', callback_data='Давай'),
                InlineKeyboardButton('Не хочу', callback_data='Не хочу'),
                InlineKeyboardButton('/help', callback_data='/help'),
            ]
        ]
        old_keyboard = ['Камень', 'Ножницы', 'Бумага']
        i = random.randint(0, 2)
        if old_keyboard[i] == 'Камень':
            answer = old_keyboard[i] + '. Ничья! Сыграем еще раз?'
        elif old_keyboard[i] == 'Ножницы':
            answer = old_keyboard[i] + '. Ты победил! Сыграем еще раз?'
        elif old_keyboard[i] == 'Бумага':
            answer = old_keyboard[i] + '. Ты проиграл! Сыграем еще раз?'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=InlineKeyboardMarkup(keyboard))

    if update.effective_message.text == 'Ножницы':
        answer = ''
        keyboard = [
            [
                # первая строчка кнопочек
                InlineKeyboardButton('Давай', callback_data='Давай'),
                InlineKeyboardButton('Не хочу', callback_data='Не хочу'),
                InlineKeyboardButton('/help', callback_data='/help'),
            ]
        ]
        old_keyboard = ['Камень', 'Ножницы', 'Бумага']
        i = random.randint(0, 2)
        if old_keyboard[i] == 'Камень':
            answer = old_keyboard[i] + '. Ты проиграл! Сыграем еще раз?'
        elif old_keyboard[i] == 'Ножницы':
            answer = old_keyboard[i] + '. Ничья! Сыграем еще раз?'
        elif old_keyboard[i] == 'Бумага':
            answer = old_keyboard[i] + '. Ты победил! Сыграем еще раз?'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=InlineKeyboardMarkup(keyboard))

    if update.effective_message.text == 'Бумага':
        answer = ''
        keyboard = [
            [
                # первая строчка кнопочек
                InlineKeyboardButton('Давай', callback_data='Давай'),
                InlineKeyboardButton('Не хочу', callback_data='Не хочу'),
                InlineKeyboardButton('/help', callback_data='/help'),
            ]
        ]
        old_keyboard = ['Камень', 'Ножницы', 'Бумага']
        i = random.randint(0, 2)
        if old_keyboard[i] == 'Камень':
            answer = old_keyboard[i] + '. Ты победил! Сыграем еще раз?'
        elif old_keyboard[i] == 'Ножницы':
            answer = old_keyboard[i] + '. Ты проиграл! Сыграем еще раз?'
        elif old_keyboard[i] == 'Бумага':
            answer = old_keyboard[i] + '. Ничья! Сыграем еще раз?'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=InlineKeyboardMarkup(keyboard))

async def call_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'Давай':
        keyboard = [['Камень', 'Ножницы', 'Бумага', '/help']]
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Отлично! Делай свой выбор!',
                                       reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                        one_time_keyboard=True))
    if query.data == 'Не хочу':
        keyboard = [['Давай']]
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Хорошо. Если, вдруг, захочешь сыграть - напиши Давай!',
                                       reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                        one_time_keyboard=True))
    if query.data == '/help':
        await help(update, context)



if __name__ == '__main__':
    application = ApplicationBuilder().token('6779250091:AAHe5HmaanIEprO5t9VAYVLIz-IlXMcbXPk').build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_processing)
    application.add_handler(message_handler)

    call_back_handler = CallbackQueryHandler(call_back)
    application.add_handler(call_back_handler)

    application.run_polling()