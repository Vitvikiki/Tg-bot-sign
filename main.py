import logging
import os
import random
import sys
import time
from threading import Thread

from dotenv import load_dotenv
from loguru import logger as log
from pydantic import BaseModel
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import MessageHandler, Filters, CallbackContext
from telegram.ext import Updater

# парсинг файла .env, и загрузка всех найденных переменных в качестве переменных среды.
from core.mark import WaterMark

load_dotenv()

log.remove()
log.add(sink=sys.stderr, level='DEBUG', enqueue=True, diagnose=True, )
log.add(sink=f"logs/marklog.log", level='TRACE', enqueue=True, encoding='utf-8', diagnose=True, )

logging.basicConfig(filename='logs/tglog.log', level=logging.DEBUG, encoding='utf-8')
# создание обработчика
updater = Updater(token=os.getenv('TOKEN'))
dispatcher = updater.dispatcher


class User(BaseModel):
    user_id: int
    state: int = 0
    # wait: bool = False

    # def __eq__(self, other: 'User' | int) -> bool:
    #     if isinstance(other, User):
    #         return self.user_id == other.user_id
    #     return self.user_id == other


class ContextStorage:
    """Хранение контекста"""

    # Словарь для хранения стадий пользователя
    USERS: dict[int, User] = {}

    @classmethod
    @log.catch
    def delay_send(cls, user_id):
        """Отложенная отправка водяного знака с текстом"""

        # Рандомный сон от 5 до 15 минут
        delay = 60 * random.randint(5, 15)
        time.sleep(delay)

        # Отправка фото
        updater.bot.send_photo(chat_id=user_id, photo=open(f'core/{user_id}.jpg', 'rb'), reply_markup=get_keyboard())

        # Сброс стадии юзера
        cls.USERS[user_id].state = 0

        # Удаление файла после отправки
        os.remove(f'core/{user_id}.jpg')

    @classmethod
    def get_message(cls, user_id: int, text: str) -> str:
        """Получение текста сообщения в зависимости от стадии пользователя"""

        # добавление в словарь при отсустсвии
        if user_id not in cls.USERS:
            cls.USERS[user_id] = User(user_id=user_id)

        # получение объекта пользователя из словаря
        user = cls.USERS.get(user_id)

        # проверка стадии пользователя
        match user.state:
            case 0:
                message = 'Введите текст водного знака (до 75 символов)'
                user.state += 1
            case 1:
                if len(text) > 76:
                    message = 'Размер текста превышает 75 символов!'
                else:
                    user.state += 1

                    # Наложение текста на водяной знак
                    water_mark = WaterMark(text, user_id)
                    water_mark.draw()

                    # Создание потока для отложенной отправки
                    Thread(target=cls.delay_send, args=(user_id,)).start()
                    message = "Вставка водного знака, ожидайте..."
            case _:
                message = "Вставка водного знака, ожидайте..."

        return message


context_storage = ContextStorage()


def get_keyboard() -> ReplyKeyboardMarkup:
    """Получить клавиатуру"""
    button = KeyboardButton('Новое сообщение')
    return ReplyKeyboardMarkup(
        [[button]],
        selective=True,
        resize_keyboard=True
    )


def message_handler(update: Update, context: CallbackContext) -> None:
    """Обработка текстовых сообщений"""
    text: str = update.message.text
    user_id: int = update.message.from_user.id

    answer: str = context_storage.get_message(user_id, text)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer,
        reply_markup=get_keyboard()
    )


# обработчик текстовых сообщений
echo_handler = MessageHandler(Filters.text & (~Filters.command), message_handler)
dispatcher.add_handler(echo_handler)

# запуск прослушивания сообщений
if __name__ == '__main__':
    updater.start_polling()
