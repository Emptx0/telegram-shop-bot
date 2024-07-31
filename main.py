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
import reply_markups
import text_templates as tt


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


@dp.message(Command("start"))
async def start(message: types.Message):
    user = usr.User(message.chat.id)
    markup_start = reply_markups.get_markup_main(user)

    await bot.send_message(
        chat_id=message.chat.id,
        text=tt.greeting,
        reply_markup=markup_start
    )


async def update_menu_text(message: types.Message, markup, msg_text):
    await message.edit_text(
        msg_text,
        reply_markup=markup
    )


@dp.callback_query(F.data.startswith("main_"))
async def callbacks_main(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "profile":
        markup = reply_markups.profile_markup(usr.User(callback.from_user.id))
        msg_text = f"Hi, <b>{callback.from_user.first_name}</b>!"
        await update_menu_text(callback.message, markup, msg_text)

    if action == "adminPanel":
        markup = reply_markups.admin_markup()
        msg_text = tt.admin_panel
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


@dp.callback_query(F.data.startswith("admin_"))
async def callbacks_admin_panel(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "userManagement":
        await callback.message.edit_text(
            text=tt.user_management+"\n\nEnter user id you want to manage:",
            reply_markup=reply_markups.back_button_markup
        )

    if action == "back":
        markup = reply_markups.get_markup_main(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


@dp.callback_query(F.data.startswith("profile_"))
async def callbacks_profile(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "back":
        markup = reply_markups.get_markup_main(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


@dp.callback_query(F.data.startswith("userManagement_"))
async def callbacks_profile(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "back":
        markup = reply_markups.admin_markup()
        msg_text = tt.admin_panel
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
