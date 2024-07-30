from aiogram import types

import text_template as text
import user as usr

# Main menu keyboard
buttons = [
    [types.InlineKeyboardButton(text=text.catalogue, callback_data="main_catalogue")],
    [types.InlineKeyboardButton(text=text.profile, callback_data="main_profile")],
    [types.InlineKeyboardButton(text=text.cart, callback_data="main_cart")]
]
admin_panel_button = [[types.InlineKeyboardButton(text=text.admin_panel, callback_data="main_adminPanel")]]
view_orders_button = [[types.InlineKeyboardButton(text=text.view_orders, callback_data="main_viewOrders")]]

# Admin Panel keyboard
admin_panel_buttons = [
    [types.InlineKeyboardButton(text=text.item_management, callback_data="admin_itemManagement")],
    [types.InlineKeyboardButton(text=text.user_management, callback_data="admin_userManagement")],
    [types.InlineKeyboardButton(text=text.back, callback_data="admin_back")]
]

# My Profile keyboard
profile_buttons = [
    [types.InlineKeyboardButton(text=text.my_orders, callback_data="profile_orders")],
    [types.InlineKeyboardButton(text=text.cancel_order, callback_data="profile_cancelOrder")],
    [types.InlineKeyboardButton(text=text.back, callback_data="profile_back")]
]


# /start
def get_markup_main(user: usr):
    if user.is_admin():
        markup = types.InlineKeyboardMarkup(inline_keyboard=admin_panel_button + buttons)
    elif user.is_manager():
        markup = types.InlineKeyboardMarkup(inline_keyboard=view_orders_button + buttons)
    else:
        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    return markup


# Admin Panel
def admin_markup():
    markup = types.InlineKeyboardMarkup(inline_keyboard=admin_panel_buttons)
    return markup


# My Profile
def profile_markup(user: usr):
    markup = types.InlineKeyboardMarkup(inline_keyboard=profile_buttons)
    return markup
