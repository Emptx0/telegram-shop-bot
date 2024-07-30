import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

import configparser
import sqlite3

from configuration import Configuration
import user as usr


config = configparser.ConfigParser()
config.read('config.ini')

configuration = Configuration()

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

bot = Bot(
    token=config['settings']['token'],
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    await dp.start_polling(bot)


@dp.message(Command("start"))
async def start(message: types.Message):
    user = usr.User(message.chat.id)

    await bot.send_message(
        chat_id=message.chat.id,
        text="<b>Welcome to test telegram shop!</b>",
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
