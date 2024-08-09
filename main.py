import asyncio
import configparser
import sqlite3
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.context import FSMContext

from configuration import Configuration
import user as usr
import states_handler as sh
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
async def start(message: types.Message, state: FSMContext):
    user = usr.User(message.chat.id, message.from_user.username)
    markup = rm.get_markup_main(user)

    await bot.send_message(
        chat_id=message.chat.id,
        text=tt.greeting,
        reply_markup=markup
    )


@dp.message(StateFilter(None), F.text)
async def chat_filter(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


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
        user = usr.User(callback.from_user.id)
        markup = rm.profile_markup(user)
        msg_text = tt.profile_info(callback.from_user.first_name, user.is_main_admin(), user.is_admin(), user.is_manager())
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
        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = f"{tt.user_management}\n\nEnter user id you want to manage:"

        await state.update_data(pr_message={"id": callback.message.message_id})
        await state.set_state(sh.AdminStates.choosing_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.get_markup_main(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


@dp.message(sh.AdminStates.choosing_user, F.text)
async def user_management(message: types.Message, state: FSMContext):
    user_id = message.text
    data = await state.get_data()
    if usr.user_exists(user_id):
        selected_user = usr.User(user_id)
        admin = usr.User(message.from_user.id)
        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(
            selected_user.get_id(), selected_user.get_username(), selected_user.is_main_admin(),
            selected_user.is_admin(), selected_user.is_manager()
        )
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message"]["id"])
        await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=markup
        )
        await state.clear()

    else:
        markup = rm.select_user_markup(usr.User(message.from_user.id))
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message"]["id"])
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"No registered users found with id <b>{user_id}</b>. Try again.",
            reply_markup=markup
        )
        await state.update_data(pr_message={"id": msg.message_id})


@dp.callback_query(F.data.startswith("um_"))
async def callbacks_user_management(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    admin = usr.User(callback.from_user.id)

    if action == "getAdmins":
        cursor.execute('SELECT user_id, username FROM Users WHERE is_admin = ?', (1,))
        admins_list = cursor.fetchall()

        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = f"{tt.get_admins_list}:\n\n"
        for user_id, username in admins_list:
            msg_text += f"{user_id} : @{username}\n"
        msg_text += "\nEnter user id you want to manage:"

        await update_menu_text(callback.message, markup, msg_text)

    if action == "getManagers":
        cursor.execute('SELECT user_id, username FROM Users WHERE is_manager = ?', (1,))
        managers_list = cursor.fetchall()

        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = f"{tt.get_managers_list}:\n\n"
        for user_id, username in managers_list:
            msg_text += f"{user_id} : @{username}\n"
        msg_text += "\nEnter user id you want to manage:"

        await update_menu_text(callback.message, markup, msg_text)

    if action == "makeAdmin":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_admin(1)
        selected_user.set_manager(0)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(
            selected_user.get_id(), selected_user.get_username(), selected_user.is_main_admin(),
            selected_user.is_admin(), selected_user.is_manager()
        )
        await update_menu_text(callback.message, markup, msg_text)

    if action == "removeAdmin":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_admin(0)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(
            selected_user.get_id(), selected_user.get_username(), selected_user.is_main_admin(),
            selected_user.is_admin(), selected_user.is_manager()
        )
        await update_menu_text(callback.message, markup, msg_text)

    if action == "makeManager":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_manager(1)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(
            selected_user.get_id(), selected_user.get_username(), selected_user.is_main_admin(),
            selected_user.is_admin(), selected_user.is_manager()
        )
        await update_menu_text(callback.message, markup, msg_text)

    if action == "removeManager":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_manager(0)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(
            selected_user.get_id(), selected_user.get_username(), selected_user.is_main_admin(),
            selected_user.is_admin(), selected_user.is_manager()
        )
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.admin_markup()
        msg_text = tt.admin_panel
        await update_menu_text(callback.message, markup, msg_text)
        await state.clear()

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
