import asyncio

import pytest
from aiogram.utils import executor
from loguru import logger

from aiogram_main import dp, bot


# @pytest.fixture()
# def start_polling():
#     executor.start_polling(dp, skip_updates=True)


@pytest.mark.asyncio
# @pytest.mark.usefixtures('event_loop')
async def test_start_polling():
    logger.info('Start')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # loop.create_task(bot.send_message(269019356, 'test'))
    await bot.send_message(269019356, 'test')
    # print(tg_user)
    # print(tg_user)
    # await executor.start_polling(dp, skip_updates=True)
