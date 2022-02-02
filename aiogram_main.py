import asyncio
import logging
import os
import random
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
from aiogram.utils import executor
from dotenv import load_dotenv
from loguru import logger as log

from core.mark import WaterMark

load_dotenv()
log.remove()
log.add(sink=sys.stderr, level='DEBUG', enqueue=True, diagnose=True, )
log.add(sink=f"logs/marklog.log", level='TRACE', enqueue=True, encoding='utf-8', diagnose=True, )

logging.basicConfig(filename='logs/aiolog.log', level=logging.DEBUG, encoding='utf-8')
# logger = logging.getLogger()
# handler = logging.StreamHandler()
# logger.addHandler(handler)

bot = Bot(token=os.getenv('TOKEN'),
          parse_mode=types.ParseMode.HTML
          )
dp = Dispatcher(bot, storage=MemoryStorage())


# хранение стадий
class Mark(StatesGroup):
    start = State()


# словарь для хранения юзеров которые уже отправили текст на наложение
WAIT_USERS = []


def get_keyboard():
    """Получение клавиатуры"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # todo
    keyboard.add('Новое сообщение')
    return keyboard


@dp.message_handler(state=Mark.start)
@log.catch
async def mark(message: types.Message, state: FSMContext):
    log.info(message.text)
    user_id = message.from_user.id

    # Проверка длинны текста
    if len(message.text) > 76:
        await message.answer('Размер текста превышает 75 символов!')
        log.warning(f'{user_id}|{message.text}. Размер текста превышает 75 символов!')

    # Если длинна текста меньше 76 символов
    else:
        await state.finish()

        # наложение текста
        water_mark = WaterMark(message.text, user_id)
        water_mark.draw()

        log.info(f'{user_id}| Вставка водного знака')
        await message.answer("Вставка водного знака, ожидайте...")

        # добавление в список ожидающих
        WAIT_USERS.append(user_id)

        # Рандомный сон от 5 до 15 минут
        delay = 60 * random.randint(5, 15)
        await asyncio.sleep(delay)

        # отправка фото
        await bot.send_photo(user_id, photo=InputFile(f'core/{user_id}.jpg', ), reply_markup=get_keyboard())

        # Удаление из списка ожидающих
        WAIT_USERS.remove(user_id)

        # удаление отправленного файла
        os.remove(f'core/{user_id}.jpg')

        log.info(f'{user_id}|Файл {user_id} удален')


@dp.message_handler()
@log.catch
async def start(message: types.Message, state: FSMContext):
    if message.from_user.id not in WAIT_USERS:
        await Mark.start.set()
        await message.answer('Введите текст водного знака (до 75 символов)')
    else:
        await message.answer("Вставка водного знака, ожидайте...")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
