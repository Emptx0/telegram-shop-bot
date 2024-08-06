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
    user = usr.User(message.chat.id)
    markup = rm.get_markup_main(user)

    await bot.send_message(
        chat_id=message.chat.id,
        text=tt.greeting,
        reply_markup=markup
    )


@dp.message(StateFilter(None), F.text)
async def chat_filter(message: types.Message):
    print(message.message_id)
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
        markup = rm.user_management_back()
        msg_text = tt.user_management+"\n\nEnter user id you want to manage:"
        await state.update_data(message_to_update=callback.message)
        await state.set_state(usr.States.choosing_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.get_markup_main(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


@dp.message(usr.States.choosing_user, F.text)
async def user_management(message: types.Message, state: FSMContext):
    user_id = message.text
    message_to_update = await state.get_data()
    if usr.user_exists(user_id):
        selected_user = usr.User(user_id)
        markup = rm.user_management_markup(selected_user)
        msg_text = (f"User id: {selected_user.get_id()}\n"
                    f"Status: %s" % ("Main Admin" if selected_user.get_id() == config.get_main_admin_id() else
                                     "Admin" if selected_user.is_admin() else
                                     "Manager" if selected_user.is_manager() else "Customer"))
        await bot.delete_message(message.chat.id, message.message_id)
        await update_menu_text(message_to_update, markup, msg_text)
        '''
        await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=markup
        )
        '''
        await state.clear()
    else:
        markup = rm.user_management_back()
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"No registered users found with id <b>{user_id}</b>. Try again.",
            reply_markup=markup
        )


@dp.callback_query(F.data.startswith("um_"))
async def callbacks_user_management(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "makeAdmin":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_admin(1)
        selected_user.set_manager(0)

        markup = rm.user_management_markup(selected_user)
        msg_text = (f"User id: <b>{selected_user.get_id()}</b>\n"
                    f"Status: %s" % ("Main Admin" if selected_user.get_id() == config.get_main_admin_id() else
                                     "Admin" if selected_user.is_admin() else
                                     "Manager" if selected_user.is_manager() else "Customer"))
        await update_menu_text(callback.message, markup, msg_text)

    if action == "removeAdmin":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_admin(0)

        markup = rm.user_management_markup(selected_user)
        msg_text = (f"User id: <b>{selected_user.get_id()}</b>\n"
                    f"Status: %s" % ("Main Admin" if selected_user.get_id() == config.get_main_admin_id() else
                                     "Admin" if selected_user.is_admin() else
                                     "Manager" if selected_user.is_manager() else "Customer"))
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
