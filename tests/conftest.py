import asyncio
from email.policy import strict

import pytest
import pytest_asyncio
from telethon import TelegramClient


# @pytest.fixture(scope='session')
# def event_loop():
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


# @pytest.fixture(scope='session')
def tg_user():
    api_id = 6517515
    api_hash = '978177284de72630e5327f6327c10043'
    client = TelegramClient('session_name', api_id, api_hash)
    return client

    # Getting information about yourself
    # async def main():
    #     me = await client.get_me()
    #     print(me)

    # with client:
    #     client.loop.run_until_complete(main())
if __name__ == '__main__':
    tg_user()