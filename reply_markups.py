from aiogram import types

import text_templates as tt
import user as usr

# Main menu keyboard
buttons = [
    [types.InlineKeyboardButton(text=tt.catalogue, callback_data="main_catalogue")],
    [types.InlineKeyboardButton(text=tt.profile, callback_data="main_profile")],
    [types.InlineKeyboardButton(text=tt.cart, callback_data="main_cart")]
]
admin_panel_button = [[types.InlineKeyboardButton(text=tt.admin_panel, callback_data="main_adminPanel")]]
view_orders_button = [[types.InlineKeyboardButton(text=tt.view_orders, callback_data="main_viewOrders")]]


# My Profile keyboard
profile_buttons = [
    [types.InlineKeyboardButton(text=tt.my_orders, callback_data="profile_orders")],
    [types.InlineKeyboardButton(text=tt.cancel_order, callback_data="profile_cancelOrder")],
    [types.InlineKeyboardButton(text=tt.back, callback_data="profile_back")]
]


# My Profile
def profile_markup(user: usr):
    markup = types.InlineKeyboardMarkup(inline_keyboard=profile_buttons)
    return markup


# Admin Panel keyboard
admin_panel_buttons = [
    [types.InlineKeyboardButton(text=tt.item_management, callback_data="admin_itemManagement")],
    [types.InlineKeyboardButton(text=tt.user_management, callback_data="admin_userManagement")],
    [types.InlineKeyboardButton(text=tt.back, callback_data="admin_back")]
]


# Admin Panel/User Management back button
back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data="userManagement_back")]]
back_button_markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)


# Admin Panel
def admin_markup():
    markup = types.InlineKeyboardMarkup(inline_keyboard=admin_panel_buttons)
    return markup


# /start
def get_markup_main(user: usr):
    if user.is_admin():
        markup = types.InlineKeyboardMarkup(inline_keyboard=admin_panel_button + buttons)
    elif user.is_manager():
        markup = types.InlineKeyboardMarkup(inline_keyboard=view_orders_button + buttons)
    else:
        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    return markup
