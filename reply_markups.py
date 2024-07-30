from aiogram import types

import text_template as text


# /start
def get_markup_default():
    buttons = [
        [types.InlineKeyboardButton(text=text.catalogue, callback_data="catalogue")],
        [types.InlineKeyboardButton(text=text.profile, callback_data="profile")],
        [types.InlineKeyboardButton(text=text.cart, callback_data="cart")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def get_markup_admin():
    buttons = [
        [types.InlineKeyboardButton(text=text.admin_panel, callback_data="admin_panel")],
        [types.InlineKeyboardButton(text=text.catalogue, callback_data="catalogue")],
        [types.InlineKeyboardButton(text=text.profile, callback_data="profile")],
        [types.InlineKeyboardButton(text=text.cart, callback_data="cart")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup
