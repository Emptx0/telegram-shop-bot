import asyncio
import configparser
import sqlite3
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.context import FSMContext

from configuration import Configuration
import user as usr
import reply_markups as rm
import text_templates as tt


configuration = configparser.ConfigParser()
configuration.read('config.ini')

config = Configuration()

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

bot = Bot(
    token=configuration['settings']['token'],
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def start(message: types.Message):
    user = usr.User(message.chat.id)
    markup = rm.get_markup_main(user)

    await bot.send_message(
        chat_id=message.chat.id,
        text=tt.greeting,
        reply_markup=markup
    )


async def update_menu_text(message: types.Message, markup, msg_text):
    await message.edit_text(
        msg_text,
        reply_markup=markup
    )


# Main menu calls
@dp.callback_query(F.data.startswith("main_"))
async def callbacks_main(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "profile":
        markup = rm.profile_markup(usr.User(callback.from_user.id))
        msg_text = (f"Hi, <b>{callback.from_user.first_name}</b>!\n"
                    f"Status: %s" % ("Admin" if usr.User(callback.from_user.id).is_admin() else
                                     "Manager" if usr.User(callback.from_user.id).is_manager() else "Customer"))
        await update_menu_text(callback.message, markup, msg_text)

    if action == "adminPanel":
        markup = rm.admin_markup()
        msg_text = tt.admin_panel
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Admin calls
@dp.callback_query(F.data.startswith("admin_"))
async def callbacks_admin_panel(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "userManagement":
        markup = rm.user_management_markup(back_button=True)
        msg_text = tt.user_management+"\n\nEnter user id you want to manage:"
        await state.set_state(usr.AdminStates.choosing_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.get_markup_main(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)
        await state.clear()

    await callback.answer()


@dp.message(usr.AdminStates.choosing_user, F.text)
async def user_chosen(message: types.Message, state: FSMContext):
    if usr.user_exists(message.text):
        markup = rm.user_management_markup(usr.User(message.text))
        msg_text = (f"User id: <b>{message.text}</b>\n"
                    f"Status: %s" % ("Main Admin" if message.text == config.get_main_admin_id() else
                                     "Admin" if usr.User(message.text).is_admin() else
                                     "Manager" if usr.User(message.text).is_manager() else "Customer"))
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=markup
        )
        await state.clear()
    else:
        markup = rm.user_management_markup(back_button=True)
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"No registered users found with id <b>{message.text}</b>. Try again.",
            reply_markup=markup
        )


@dp.callback_query(F.data.startswith("userManagement_"))
async def callbacks_profile(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "back":
        markup = rm.admin_markup()
        msg_text = tt.admin_panel
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Profile calls
@dp.callback_query(F.data.startswith("profile_"))
async def callbacks_profile(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "back":
        markup = rm.get_markup_main(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
