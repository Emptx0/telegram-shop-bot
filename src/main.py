import asyncio
import configparser
import sqlite3
import logging
import os
from random import randint

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.types import LinkPreviewOptions, FSInputFile

from configuration import Configuration
import user as usr
import states_handler as sh
import reply_markups as rm
import text_templates as tt
import category
import item as itm
import order as ordr
import cryptopay as cp


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
    user = usr.User(message.chat.id, message.from_user.username)
    markup = rm.main_menu_markup(user)

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

    if action == "adminPanel":
        markup = rm.admin_markup()
        msg_text = tt.admin_panel
        await update_menu_text(callback.message, markup, msg_text)

    if action == "viewOrders":
        cursor.execute('SELECT order_id FROM orders')
        order_list = list(cursor.fetchall())
        markup = rm.get_orders_markup(order_list)
        msg_text = tt.view_orders
        await update_menu_text(callback.message, markup, msg_text)

    if action == "catalogue":
        cursor.execute('SELECT id, name FROM categories')
        cat_list = cursor.fetchall()

        markup = rm.catalogue_cats_markup(cat_list)
        msg_text = (f"{tt.catalogue}\n\n"
                    f"Select category:")
        await update_menu_text(callback.message, markup, msg_text)

    if action == "profile":
        user = usr.User(callback.from_user.id)
        markup = rm.profile_markup()
        msg_text = tt.profile_info(callback.from_user.first_name, user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "cart":
        user = usr.User(callback.from_user.id)
        if not user.get_cart():
            markup = rm.back_to_main_menu()
            msg_text = (f"{tt.cart}:\n\n"
                        f"Your cart is empty.")
        else:
            markup = rm.get_cart_markup(user.get_cart())
            msg_text = (f"{tt.cart}:\n"
                        f"Price - <b>{user.get_cart_price()}</b>")
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
        markup = rm.main_menu_markup(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Item management callback handler
@dp.callback_query(F.data.startswith("im_"))
async def callbacks_item_management(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    # Categories management
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
        cat_list = cursor.fetchall()

        markup = rm.select_cat_markup()
        msg_text = tt.get_cats(cat_list)

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

    if action == "addItem":
        selected_cat_id = callback.data.split("_")[2]
        markup = rm.select_item_markup(selected_cat_id, back=True)
        msg_text = f"{tt.add_item[0]}\n\nEnter name of the item you want to add:"

        await state.update_data(pr_message_id=callback.message.message_id, cat_id=selected_cat_id)
        await state.set_state(sh.AdminStates.add_item_name)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "manageItems":
        cat_id = callback.data.split("_")[2]
        markup = rm.select_item_markup(cat_id)
        msg_text = f"{tt.manage_items}\n\nEnter ID of the item you want to manage:"

        await state.update_data(pr_message_id=callback.message.message_id, cat_id=cat_id)
        await state.set_state(sh.AdminStates.choosing_item)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        cursor.execute('SELECT id, name FROM categories')
        cat_list = cursor.fetchall()

        markup = rm.select_cat_markup()
        msg_text = tt.get_cats(cat_list)

        await state.update_data(pr_message_id=callback.message.message_id)
        await state.set_state(sh.AdminStates.choosing_cat)
        await update_menu_text(callback.message, markup, msg_text)


    # Items management
    if action == "getItems":
        cat_id = callback.data.split("_")[2]
        cursor.execute('SELECT id, name FROM items WHERE cat_id=?', [cat_id])
        item_list = cursor.fetchall()

        markup = rm.select_item_markup(cat_id)
        msg_text = tt.get_items(item_list)

        await update_menu_text(callback.message, markup, msg_text)

    if action == "renameItem":
        selected_item_id = callback.data.split("_")[2]
        markup = rm.item_management_back(selected_item_id)
        msg_text = f"{tt.rename_item[0]}\n\nEnter new name for the item:"

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            item_id=selected_item_id
        )
        await state.set_state(sh.AdminStates.changing_item_name)

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            msg = await bot.send_message(
                chat_id=data["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message_id=msg.message_id)

    if action == "changePrice":
        selected_item_id = callback.data.split("_")[2]
        markup = rm.item_management_back(selected_item_id)
        msg_text = f"{tt.change_price[0]}\n\nEnter new price for the item in $:"

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            item_id=selected_item_id
        )
        await state.set_state(sh.AdminStates.changing_item_price)

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            msg = await bot.send_message(
                chat_id=data["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message_id=msg.message_id)

    if action == "changeDesc":
        selected_item_id = callback.data.split("_")[2]
        markup = rm.item_management_back(selected_item_id)
        msg_text = f"{tt.change_desc[0]}\n\nEnter new description for the item:"

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            item_id=selected_item_id
        )
        await state.set_state(sh.AdminStates.changing_item_desc)

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            msg = await bot.send_message(
                chat_id=data["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message_id=msg.message_id)

    if action == "changeAmount":
        selected_item_id = callback.data.split("_")[2]
        markup = rm.item_management_back(selected_item_id)
        msg_text = f"{tt.change_amount[0]}\n\nEnter amount for the items:"

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            item_id=selected_item_id
        )
        await state.set_state(sh.AdminStates.changing_item_amount)

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            msg = await bot.send_message(
                chat_id=data["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message_id=msg.message_id)

    if action == "uploadImg":
        selected_item_id = callback.data.split("_")[2]
        markup = rm.item_management_back(selected_item_id)
        msg_text = f"{tt.upload_image[0]}\n\nSend image you want to upload:"

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            item_id=selected_item_id
        )
        await state.set_state(sh.AdminStates.image_uploading)

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            msg = await bot.send_message(
                chat_id=data["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message_id=msg.message_id)

    if action == "deleteImg":
        selected_item = itm.Item(callback.data.split("_")[2])
        if not selected_item.get_image_id() == 0:
            os.remove(selected_item.get_image_path())
        selected_item.set_image_id(0)
        markup = rm.item_management_back(selected_item.get_id())
        msg_text = tt.delete_image[1]

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            item_id=selected_item.get_id()
        )
        await state.set_state(sh.AdminStates.deleting_item)

        try:
            await update_menu_text(callback.message, markup, msg_text)
            await state.clear()
        except:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            await bot.send_message(
                chat_id=data["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.clear()

    if action == "deleteItem":
        selected_item = itm.Item(callback.data.split("_")[2])
        markup = rm.select_item_markup(selected_item.get_cat_id(), back=True)
        msg_text = tt.delete_item[1]
        selected_item.delete()

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            item_id=selected_item.get_id()
        )
        await state.set_state(sh.AdminStates.deleting_item)

        try:
            await update_menu_text(callback.message, markup, msg_text)
            await state.clear()
        except:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            await bot.send_message(
                chat_id=data["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.clear()

    if action == "backToCat":
        cat_id = callback.data.split("_")[2]

        cat = category.Category(cat_id)
        markup = rm.cat_management_markup(cat.get_id())
        msg_text = tt.cat_info(cat.get_id(), cat.get_name())

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])
            await bot.send_message(
                chat_id=data["pr_message"]["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.clear()

    if action == "backToItem":
        item_id = callback.data.split("_")[2]
        item = itm.Item(item_id)
        markup = rm.item_management_markup(item.get_id(), item.get_cat_id())
        msg_text = tt.item_info(item)

        if item.get_image_id() == 0:
            await update_menu_text(callback.message, markup, msg_text)
            await state.clear()
        else:
            data = await state.get_data()
            await bot.delete_message(data["chat_id"], data["pr_message_id"])
            msg = await bot.send_photo(
                chat_id=data["chat_id"],
                photo=FSInputFile(item.get_image_path()),
                caption=msg_text,
                reply_markup=markup
            )
            await state.clear()
            await state.set_state(sh.AdminStates.choosing_item)
            await state.update_data(pr_message={"chat_id": msg.chat.id, "id": msg.message_id})

    await callback.answer()


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
    while True:
        cat_id = randint(100000, 999999)
        if not category.category_exist(cat_id):
            break
    cat = category.Category(cat_id)
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


# Category management
@dp.message(sh.AdminStates.renaming_cat, F.text)
async def cat_renaming(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat = category.Category(data["cat_id"])
    cat.set_name(message.text)

    markup = rm.cat_management_back()
    msg_text = tt.rename_cat[1]
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
        markup = rm.item_management_markup(item.get_id(), item.get_cat_id())
        msg_text = tt.item_info(item)
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])

        if item.get_image_id() == 0:
            await bot.send_message(
                chat_id=message.chat.id,
                text=msg_text,
                reply_markup=markup
            )
            await state.clear()
        else:
            msg = await bot.send_photo(
                chat_id=message.chat.id,
                photo=FSInputFile(item.get_image_path()),
                caption=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message={"chat_id": msg.chat.id, "id": msg.message_id})

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


@dp.message(sh.AdminStates.add_item_name, F.text)
async def item_name(message: types.Message, state: FSMContext):
    data = await state.get_data()

    markup = rm.select_item_markup(data["cat_id"], back=True)
    msg_text = "Enter item price in $:"
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=msg_text,
        reply_markup=markup
    )
    await state.update_data(pr_message_id=msg.message_id, item_name=message.text)
    await state.set_state(sh.AdminStates.add_item_price)


@dp.message(sh.AdminStates.add_item_price, F.text)
async def item_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price = message.text

    try:
        float(price)
        while True:
            item_id = randint(100000, 999999)
            if not itm.item_exist(item_id):
                break
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
            text=f"The price must be a digital value! Try again.",
            reply_markup=markup
        )
        await state.update_data(pr_message_id=msg.message_id)


# Item management
@dp.message(sh.AdminStates.changing_item_name, F.text)
async def changing_item_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = itm.Item(data["item_id"])
    item.set_name(message.text)

    markup = rm.item_management_back(item.get_id())
    msg_text = tt.rename_item[1]
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=data["chat_id"],
        text=msg_text,
        reply_markup=markup
    )
    await state.update_data(pr_message_id=msg.message_id)


@dp.message(sh.AdminStates.changing_item_price, F.text)
async def changing_item_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = itm.Item(data["item_id"])
    price = message.text

    try:
        float(price)
        item.set_price(price)

        markup = rm.item_management_back(item.get_id())
        msg_text = tt.change_price[1]
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        msg = await bot.send_message(
            chat_id=data["chat_id"],
            text=msg_text,
            reply_markup=markup
        )
        await state.update_data(pr_message_id=msg.message_id)

    except ValueError:
        markup = rm.item_management_back(item.get_id())
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data["pr_message_id"])
        msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"The price must be a digital value! Try again.",
            reply_markup=markup
        )
        await state.update_data(pr_message_id=msg.message_id)


@dp.message(sh.AdminStates.changing_item_desc, F.text)
async def changing_item_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = itm.Item(data["item_id"])
    item.set_desc(message.text)

    markup = rm.item_management_back(item.get_id())
    msg_text = tt.change_desc[1]
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=data["chat_id"],
        text=msg_text,
        reply_markup=markup
    )
    await state.update_data(pr_message_id=msg.message_id)


@dp.message(sh.AdminStates.changing_item_amount, F.text)
async def changing_item_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = itm.Item(data["item_id"])
    item.set_amount(message.text)

    markup = rm.item_management_back(item.get_id())
    msg_text = tt.change_amount[1]
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=data["chat_id"],
        text=msg_text,
        reply_markup=markup
    )
    await state.update_data(pr_message_id=msg.message_id)


@dp.message(sh.AdminStates.image_uploading, F.photo)
async def image_uploading(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = itm.Item(data["item_id"])
    image_id = message.message_id
    if not item.get_image_id() == 0:
        os.remove(item.get_image_path())
    item.set_image_id(image_id)

    await message.bot.download(file=message.photo[-1].file_id, destination=item.get_image_path())

    markup = rm.item_management_back(item.get_id())
    msg_text = tt.upload_image[1]
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=data["chat_id"],
        text=msg_text,
        reply_markup=markup
    )
    await state.update_data(pr_message_id=msg.message_id)


# User management
@dp.message(sh.AdminStates.choosing_user, F.text)
async def user_management(message: types.Message, state: FSMContext):
    user_id = message.text
    data = await state.get_data()

    if usr.user_exist(user_id):
        selected_user = usr.User(user_id)
        admin = usr.User(message.from_user.id)
        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(selected_user)
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
        cursor.execute('SELECT user_id, username FROM users WHERE is_admin=?', (1,))
        admin_list = cursor.fetchall()

        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = tt.get_admin_list + tt.get_users(admin_list)

        await update_menu_text(callback.message, markup, msg_text)

    if action == "getManagers":
        cursor.execute('SELECT user_id, username FROM users WHERE is_manager=?', (1,))
        manager_list = cursor.fetchall()

        markup = rm.select_user_markup(usr.User(callback.from_user.id))
        msg_text = tt.get_manager_list + tt.get_users(manager_list)

        await update_menu_text(callback.message, markup, msg_text)

    if action == "makeAdmin":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_admin(1)
        selected_user.set_manager(0)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(selected_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "removeAdmin":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_admin(0)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(selected_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "makeManager":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_manager(1)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(selected_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "removeManager":
        selected_user = usr.User(callback.data.split("_")[2])
        selected_user.set_manager(0)

        markup = rm.user_management_markup(selected_user, admin.is_main_admin())
        msg_text = tt.user_info(selected_user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.admin_markup()
        msg_text = tt.admin_panel
        await update_menu_text(callback.message, markup, msg_text)
        await state.clear()

    await callback.answer()


# View Orders callback handler
@dp.callback_query(F.data.startswith("management_"))
async def callbacks_management(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "viewOrder":
        order = ordr.Order(callback.data.split("_")[2])
        markup = rm.order_management_markup(order.get_id())
        msg_text = tt.order_info(order)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "processing":
        order = ordr.Order(callback.data.split("_")[2])
        order.set_status(0)
        markup = rm.order_management_markup(order.get_id())
        msg_text = tt.order_info(order)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "delivered":
        order = ordr.Order(callback.data.split("_")[2])
        order.set_status(1)
        markup = rm.order_management_markup(order.get_id())
        msg_text = tt.order_info(order)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "done":
        order = ordr.Order(callback.data.split("_")[2])
        order.set_status(2)
        markup = rm.order_management_markup(order.get_id())
        msg_text = tt.order_info(order)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "delivered":
        order = ordr.Order(callback.data.split("_")[2])
        order.set_status(1)
        markup = rm.order_management_markup(order.get_id())
        msg_text = tt.order_info(order)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "canceled":
        order = ordr.Order(callback.data.split("_")[2])
        order.set_status(-1)
        markup = rm.order_management_markup(order.get_id())
        msg_text = tt.order_info(order)
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Catalogue callback handler
@dp.callback_query(F.data.startswith("cat_"))
async def callbacks_catalogue(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "viewCat":
        cat_id = callback.data.split("_")[2]
        cursor.execute('SELECT id, name, price FROM items WHERE cat_id=?', [cat_id])
        item_list = cursor.fetchall()

        markup = rm.catalogue_items_markup(item_list)
        msg_text = (f"{tt.catalogue}\n\n"
                    f"Select item:")

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])
            await bot.send_message(
                chat_id=data["pr_message"]["chat_id"],
                text=msg_text,
                reply_markup=markup
            )

    if action == "viewItem":
        item_id = callback.data.split("_")[2]
        item = itm.Item(item_id)

        markup = rm.item_markup(item.get_id(), item.get_cat_id())
        msg_text = tt.item(item)
        await state.set_state(sh.CustomerStates.viewing_item)
        await state.update_data(pr_message={"chat_id": callback.message.chat.id, "id": callback.message.message_id})

        if item.get_image_id() == 0:
            await update_menu_text(callback.message, markup, msg_text)
        else:
            data = await state.get_data()
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])
            msg = await bot.send_photo(
                chat_id=data["pr_message"]["chat_id"],
                photo=FSInputFile(item.get_image_path()),
                caption=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message={"chat_id": msg.chat.id, "id": msg.message_id})

    if action == "addToCart":
        item_id = callback.data.split("_")[2]
        selected_item = itm.Item(item_id)

        markup = rm.back_to_item_markup(item_id)
        msg_text = (f"<i>{selected_item.get_amount()} available</i>"
                    "\nEnter amount:")

        try:
            await update_menu_text(callback.message, markup, msg_text)
            await state.update_data(
                pr_message={"chat_id": callback.message.chat.id, "id": callback.message.message_id},
                item_id=item_id
            )
            await state.set_state(sh.CustomerStates.add_to_cart)
        except:
            data = await state.get_data()
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])
            msg = await bot.send_message(
                chat_id=data["pr_message"]["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.update_data(
                pr_message={"chat_id": msg.chat.id, "id": msg.message_id},
                item_id=item_id
            )

        await state.set_state(sh.CustomerStates.add_to_cart)

    if action == "back":
        markup = rm.main_menu_markup(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Viewing item
@dp.message(sh.CustomerStates.viewing_item)
async def item_view_chat_filter(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


# Add to cart
@dp.message(sh.CustomerStates.add_to_cart, F.text)
async def get_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = message.text
    item = itm.Item(data["item_id"])

    try:
        int(amount)
        if 0 <= int(amount) <= item.get_amount():
            user = usr.User(message.from_user.id)
            user.add_to_cart(item.get_id(), amount)

            markup = rm.back_to_item_markup(item.get_id())
            msg_text = tt.add_to_cart[1]

            await bot.delete_message(message.chat.id, message.message_id)
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])

            await bot.send_message(
                chat_id=data["pr_message"]["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
        else:
            markup = rm.back_to_item_markup(item.get_id())
            msg_text = (f"<i>{item.get_amount()} available</i>"
                        "\nPlease enter a valid value:")

            await bot.delete_message(message.chat.id, message.message_id)
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])

            msg = await bot.send_message(
                chat_id=data["pr_message"]["chat_id"],
                text=msg_text,
                reply_markup=markup
            )
            await state.update_data(
                pr_message={"chat_id": msg.chat.id, "id": msg.message_id},
                item_id=item.get_id()
            )
    except ValueError:
        markup = rm.back_to_item_markup(item.get_id())
        msg_text = (f"<i>{item.get_amount()} available</i>"
                    "\nPlease enter a valid value:")

        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])

        msg = await bot.send_message(
            chat_id=data["pr_message"]["chat_id"],
            text=msg_text,
            reply_markup=markup
        )
        await state.update_data(
            pr_message={"chat_id": msg.chat.id, "id": msg.message_id},
            item_id=item.get_id()
        )


# User profile callback handler
@dp.callback_query(F.data.startswith("profile_"))
async def callbacks_profile(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "orders":
        user = usr.User(callback.from_user.id)
        if not user.get_orders():
            markup = rm.back_to_main_menu()
            msg_text = (f"{tt.my_orders}:\n\n"
                        f"You have no orders yet.")
        else:
            markup = rm.get_user_orders_markup(user.get_orders())
            msg_text = f"{tt.my_orders}:"
        await update_menu_text(callback.message, markup, msg_text)

    if action == "viewOrder":
        order = ordr.Order(callback.data.split("_")[2])
        markup = rm.order_markup(order.get_id(), order.get_status())
        msg_text = tt.order_info(order)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "cancelOrder":
        order = ordr.Order(callback.data.split("_")[2])
        order.set_status(-1)
        markup = rm.back_to_profile()
        msg_text = tt.cancel_order[1]
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back_to_profile":
        user = usr.User(callback.from_user.id)
        markup = rm.profile_markup()
        msg_text = tt.profile_info(callback.from_user.first_name, user)
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.main_menu_markup(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Cart callback handler
@dp.callback_query(F.data.startswith("cart_"))
async def callbacks_cart(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "viewItem":
        item = itm.Item(callback.data.split("_")[2])
        markup = rm.cart_item_view_markup(item.get_id())
        msg_text = tt.cart_item_info(item, callback.data.split("_")[3])
        await state.set_state(sh.CustomerStates.viewing_item)
        await state.update_data(pr_message={"chat_id": callback.message.chat.id, "id": callback.message.message_id})

        if item.get_image_id() == 0:
            await update_menu_text(callback.message, markup, msg_text)
        else:
            data = await state.get_data()
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])
            msg = await bot.send_photo(
                chat_id=data["pr_message"]["chat_id"],
                photo=FSInputFile(item.get_image_path()),
                caption=msg_text,
                reply_markup=markup
            )
            await state.update_data(pr_message={"chat_id": msg.chat.id, "id": msg.message_id})

    if action == "removeItem":
        item = itm.Item(callback.data.split("_")[2])
        user = usr.User(callback.from_user.id)
        user.remove_from_cart(item.get_id())

        markup = rm.back_to_cart()
        msg_text = tt.cart_remove_item[1]

        try:
            await update_menu_text(callback.message, markup, msg_text)
            await state.clear()
        except:
            data = await state.get_data()
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])
            await bot.send_message(
                chat_id=data["pr_message"]["chat_id"],
                text=msg_text,
                reply_markup=markup
            )

    if action == "makeOrder":
        markup = rm.back_to_cart()
        msg_text = "Enter your email address:"

        await state.update_data(
            pr_message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
        )
        await state.set_state(sh.CustomerStates.email_address)

        await update_menu_text(callback.message, markup, msg_text)

    if action == "backToCart":
        user = usr.User(callback.from_user.id)
        if not user.get_cart():
            markup = rm.back_to_main_menu()
            msg_text = (f"{tt.cart}:\n\n"
                        f"Your cart is empty.")
        else:
            markup = rm.get_cart_markup(user.get_cart())
            msg_text = (f"{tt.cart}:\n"
                        f"Price - <b>{user.get_cart_price()}</b>")

        try:
            await update_menu_text(callback.message, markup, msg_text)
        except:
            data = await state.get_data()
            await bot.delete_message(data["pr_message"]["chat_id"], data["pr_message"]["id"])
            await bot.send_message(
                chat_id=data["pr_message"]["chat_id"],
                text=msg_text,
                reply_markup=markup
            )

        await state.clear()

    if action == "payWithUSDT":
        user = usr.User(callback.from_user.id)

        currency = "USDT"
        invoice_url, invoice_id = await cp.CryptoPay.create_invoice(user.get_cart_price(), currency)

        markup = rm.payment_markup(invoice_url, invoice_id)
        msg_text = tt.complete_payment
        await update_menu_text(callback.message, markup, msg_text)

    if action == "payWithTON":
        user = usr.User(callback.from_user.id)

        currency = "TON"
        invoice_url, invoice_id = await cp.CryptoPay.create_invoice(user.get_cart_price(), currency)

        markup = rm.payment_markup(invoice_url, invoice_id)
        msg_text = tt.complete_payment
        await update_menu_text(callback.message, markup, msg_text)

    if action == "back":
        markup = rm.main_menu_markup(usr.User(callback.from_user.id))
        msg_text = tt.greeting
        await update_menu_text(callback.message, markup, msg_text)

    await callback.answer()


# Place Order
@dp.message(sh.CustomerStates.email_address, F.text)
async def get_user_email_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(email_address=message.text)

    markup = rm.back_to_cart()
    msg_text = "Enter your home address:"
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=msg_text,
        reply_markup=markup
    )
    await state.update_data(pr_message_id=msg.message_id)
    await state.set_state(sh.CustomerStates.home_address)


@dp.message(sh.CustomerStates.home_address, F.text)
async def get_user_home_address(message: types.Message, state: FSMContext):
    markup = rm.select_currency_markup()
    msg_text = tt.select_currency

    data = await state.get_data()
    await state.update_data(home_address=message.text)
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(message.chat.id, data["pr_message_id"])
    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=msg_text,
        reply_markup=markup
    )

    await state.update_data(pr_message_id=msg.message_id)
    await state.set_state(sh.CustomerStates.payment)


# Check Payment
@dp.callback_query(F.data.startswith("payment_"))
async def payment_check(callback: types.CallbackQuery, state: FSMContext):
    invoice_id = int(callback.data.split("_")[1])
    status = await cp.CryptoPay.get_status(invoice_id)

    if status == "active":
        await callback.answer("⌚️ We have not received your payment yet")
    elif status == "paid":
        data = await state.get_data()
        user = usr.User(callback.from_user.id)

        while True:
            order_id = randint(100000, 999999)
            if not ordr.order_exist(order_id):
                break
        ordr.create_order(order_id, user.get_id(), user.get_cart_comma(), data["email_address"], data["home_address"])
        for item in user.get_cart():
            user.remove_from_cart(item.get_id())
        await state.clear()

        await callback.answer("✅ Successful payment, we processing your order!")

        markup = rm.get_user_orders_markup(user.get_orders())
        msg_text = f"{tt.my_orders}:"
        await update_menu_text(callback.message, markup, msg_text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
