import os
from uuid import uuid4

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler

load_dotenv()


def put(update, context):
    """Usage: /put value"""
    # генерируем идентификатор
    key = str(uuid4())
    # Здесь не используется context.args,
    # т.к. значение может содержать пробелы.
    value = update.message.text.partition(' ')[2]

    # сохраняем значение в контекст
    context.user_data[key] = value
    # отправляем ключ пользователю
    update.message.reply_text(key)


def get(update, context):
    """Usage: /get uuid"""
    # отделяем идентификатор от команды
    key = context.args[0]

    # загружаем значение и отправляем пользователю
    value = context.user_data.get(key, 'Not found')
    update.message.reply_text(value)


if __name__ == '__main__':
    updater = Updater(os.getenv('TOKEN'), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('put', put))
    dp.add_handler(CommandHandler('get', get))

    updater.start_polling()
    updater.idle()
