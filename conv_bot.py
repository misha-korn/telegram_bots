import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

conn = sqlite3.connect('conv_db.sqlite3')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                                id INT PRIMARY KEY,
                                name TEXT,
                                photo_path TEXT,
                                about TEXT);''')
conn.commit()

NAME, PHOTO, ABOUT = range(1, 4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Как мне к вам обращаться?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'User {update.effective_user.username} name — {update.message.text}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пришлите вашу аватарку")
    context.user_data['name'] = update.message.text
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(f'./user_pic/user_{update.effective_user.username}.jpg')
    logger.info(f'User {update.effective_user.username} photo getted')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Расскажите о себе")
    context.user_data['photo'] = f'./user_pic/user_{update.effective_user.username}.jpg'
    return ABOUT

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Расскажите о себе")
    context.user_data['photo'] = None
    return ABOUT


async def get_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Cпасибо за регистрацию!')
    cursor.execute(f'INSERT INTO users VALUES({update.effective_user.id}, {context.user_data["name"]},'
                   f' {context.user_data["photo"]},'
                   f'{update.message.text})')
    conn.commit()
    return ConversationHandler.END



if __name__ == '__main__':
    application = ApplicationBuilder().token(config['token']).build()

    conv_hand = ConversationHandler(
                        entry_points=[CommandHandler('start', start)],
                        states={
                            NAME: [MessageHandler(filters.TEXT, get_name)],
                            PHOTO: [MessageHandler(filters.PHOTO, get_photo), MessageHandler(filters.Regex('^пропустить$'),skip)],
                            ABOUT: [MessageHandler(filters.TEXT, get_about)]
                        },
                        fallbacks=[]
    )

    application.add_handler(conv_hand)
    
    application.run_polling()