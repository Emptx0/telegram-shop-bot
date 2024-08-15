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
from aiogram.types import LinkPreviewOptions

from configuration import Configuration
import user as usr
import states_handler as sh
import reply_markups as rm
import text_templates as tt
import category
import item as itm


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
        text=tt.myGitHub,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )

    await bot.send_message(
        chat_id=message.chat.id,
        text=tt.greeting,
        reply_markup=markup
    )


@dp.message(StateFilter(None))
async def chat_filter(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


async def update_menu_text(message: types.Message, markup, msg_text):
    await message.edit_text(
        msg_text,
        reply_markup=markup
    )


# Main menu callback handler
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


# Admin panel callback handler
@dp.callback_query(F.data.startswith("admin_"))
async def callbacks_admin_panel(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "itemManagement":
        markup = rm.item_management_panel_markup()
        msg_text = tt.item_management
        await update_menu_text(callback.message, markup, msg_text)

    if action == "userManagement":
        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = f"{tt.user_management}\n\nEnter user ID you want to manage:"

        await state.update_data(pr_message_id=callback.message.message_id)
        await state.set_state(sh.AdminStates.choosing_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.get_markup_main(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Item management callback handler
@dp.callback_query(F.data.startswith("im_"))
async def callbacks_item_management(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "selectCat":
        markup = rm.select_cat_markup()
        msg_text = f"{tt.select_cat}\n\nEnter ID of the category you want to manage:"

        await state.update_data(pr_message_id=callback.message.message_id)
        await state.set_state(sh.AdminStates.choosing_cat)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "createCat":
        markup = rm.item_management_panel_markup(back=True)
        msg_text = f"{tt.create_cat[0]}\n\nEnter name of the category you want to create:"

        await state.update_data(pr_message_id=callback.message.message_id)
        await state.set_state(sh.AdminStates.creating_cat)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "getCats":
        cursor.execute('SELECT id, name FROM categories')
        cats_list = cursor.fetchall()

        markup = rm.select_cat_markup()
        msg_text = tt.get_cats(cats_list)

        await update_menu_text(callback.message, markup, msg_text)

    if action == "manageItems":
        cat_id = callback.data.split("_")[2]
        markup = rm.select_item_markup(cat_id)
        msg_text = f"{tt.manage_items}\n\nEnter ID of the item you want to manage:"

        await state.update_data(pr_message_id=callback.message.message_id, cat_id=cat_id)
        await state.set_state(sh.AdminStates.choosing_item)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "getItems":
        cat_id = callback.data.split("_")[2]
        cursor.execute('SELECT id, name FROM items WHERE cat_id=?', [cat_id])
        items_list = cursor.fetchall()

        markup = rm.select_item_markup(cat_id)
        msg_text = tt.get_items(items_list)

        await update_menu_text(callback.message, markup, msg_text)

    if action == "selectItemBack":
        cat_id = callback.data.split("_")[2]

        cat = category.Category(cat_id)
        markup = rm.cat_management_markup(cat.get_id())
        msg_text = tt.cat_info(cat.get_id(), cat.get_name())

        await update_menu_text(callback.message, markup, msg_text)
        await state.clear()

    if action == "addItem":
        selected_cat_id = callback.data.split("_")[2]
        markup = rm.select_item_markup(selected_cat_id, back=True)
        msg_text = f"{tt.add_item[0]}\n\nEnter name of the item you want to add:"

        await state.update_data(pr_message_id=callback.message.message_id, cat_id=selected_cat_id)
        await state.set_state(sh.AdminStates.item_name)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "renameCat":
        selected_cat_id = callback.data.split("_")[2]
        markup = rm.cat_management_back()
        msg_text = f"{tt.rename_cat[0]}\n\nEnter new name for the category:"

        await state.update_data(pr_message_id=callback.message.message_id, cat_id=selected_cat_id)
        await state.set_state(sh.AdminStates.renaming_cat)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "deleteCat":
        selected_cat = category.Category(callback.data.split("_")[2])
        selected_cat.delete()

        markup = rm.cat_management_back()
        msg_text = tt.delete_cat[1]
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        cursor.execute('SELECT id, name FROM categories')
        cats_list = cursor.fetchall()

        markup = rm.select_cat_markup()
        msg_text = tt.get_cats(cats_list)

        await state.update_data(pr_message_id=callback.message.message_id)
        await state.set_state(sh.AdminStates.choosing_cat)
        await update_menu_text(callback.message, markup, msg_text)


# Category select/add
@dp.message(sh.AdminStates.choosing_cat, F.text)
async def cat_management(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat_id = message.text

    if category.category_exist(cat_id):
        cat = category.Category(cat_id)
        markup = rm.cat_management_markup(cat.get_id())
        msg_text = tt.cat_info(cat.get_id(), cat.get_name())
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=markup
        )
        await state.clear()

    else:
        markup = rm.select_cat_markup()
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"No categories found with ID <b>{cat_id}</b>. Try again.",
            reply_markup=markup
        )
        await state.update_data(pr_message_id=msg.message_id)


@dp.message(sh.AdminStates.creating_cat, F.text)
async def cat_creating(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat = category.Category(message.message_id)
    category.create_cat(cat.get_id(), message.text)

    markup = rm.cat_management_back()
    msg_text = tt.create_cat[1]
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    await bot.send_message(
        chat_id=message.chat.id,
        text=msg_text,
        reply_markup=markup
    )
    await state.clear()


# Item select/add
@dp.message(sh.AdminStates.choosing_item, F.text)
async def item_management(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item_id = message.text

    if itm.item_exist(item_id):
        item = itm.Item(item_id)
        markup = rm.item_management_markup(item.get_id())
        msg_text = tt.item_info(item)
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])

        if item.get_image_id() == 0:
            await bot.send_message(
                chat_id=message.chat.id,
                text=msg_text,
                reply_markup=markup
            )
        else:
            await bot.send_message(            # TODO add image to message
                chat_id=message.chat.id,
                text=msg_text,
                reply_markup=markup
            )

        await state.clear()

    else:
        markup = rm.select_item_markup(data["cat_id"])
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"No items found with ID <b>{item_id}</b>. Try again.",
            reply_markup=markup
        )
        await state.update_data(pr_message_id=msg.message_id)


@dp.message(sh.AdminStates.item_name, F.text)
async def item_name(message: types.Message, state: FSMContext):
    data = await state.get_data()

    markup = rm.select_item_markup(data["cat_id"], back=True)
    msg_text = "Enter item price:"
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=msg_text,
        reply_markup=markup
    )
    await state.update_data(pr_message_id=msg.message_id, item_name=message.text)
    await state.set_state(sh.AdminStates.item_price)


@dp.message(sh.AdminStates.item_price, F.text)
async def item_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price = message.text

    try:
        float(price)
        itm.create_item(message.message_id, data["item_name"], price, data["cat_id"])

        markup = rm.select_item_markup(data["cat_id"], back=True)
        msg_text = tt.add_item[1]
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=markup
        )
        await state.clear()

    except ValueError:
        markup = rm.cat_management_back()
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"The price must be indicated as a digital value! Try again.",
            reply_markup=markup
        )
        await state.update_data(pr_message_id=msg.message_id)


# Category management
@dp.message(sh.AdminStates.renaming_cat, F.text)
async def cat_renaming(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat = category.Category(data["cat_id"]["id"])
    cat.set_name(message.text)

    markup = rm.item_management_panel_markup(back=True)
    msg_text = tt.rename_cat[1]
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    await bot.send_message(
        chat_id=message.chat.id,
        text=msg_text,
        reply_markup=markup
    )
    await state.clear()


# User management
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
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text,
            reply_markup=markup
        )
        await state.clear()

    else:
        markup = rm.select_user_markup(usr.User(message.from_user.id))
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"No registered users found with ID <b>{user_id}</b>. Try again.",
            reply_markup=markup
        )
        await state.update_data(pr_message_id=msg.message_id)


# User management callback handler
@dp.callback_query(F.data.startswith("um_"))
async def callbacks_user_management(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    admin = usr.User(callback.from_user.id)

    if action == "getAdmins":
        cursor.execute('SELECT user_id, username FROM users WHERE is_admin = ?', (1,))
        admins_list = cursor.fetchall()

        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = tt.get_admins_list + tt.get_users(admins_list)

        await update_menu_text(callback.message, markup, msg_text)

    if action == "getManagers":
        cursor.execute('SELECT user_id, username FROM users WHERE is_manager = ?', (1,))
        managers_list = cursor.fetchall()

        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = tt.get_managers_list + tt.get_users(managers_list)

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


# User profile callback handler
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
