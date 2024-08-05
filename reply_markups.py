from aiogram import types

import text_templates as tt
import user as usr


# /start
def get_markup_main(user: usr):
    main_buttons = [
        [types.InlineKeyboardButton(text=tt.catalogue, callback_data="main_catalogue")],
        [types.InlineKeyboardButton(text=tt.profile, callback_data="main_profile")],
        [types.InlineKeyboardButton(text=tt.cart, callback_data="main_cart")]
    ]
    admin_panel_button = [[types.InlineKeyboardButton(text=tt.admin_panel, callback_data="main_adminPanel")]]
    view_orders_button = [[types.InlineKeyboardButton(text=tt.view_orders, callback_data="main_viewOrders")]]

    if user.is_admin():
        markup = types.InlineKeyboardMarkup(inline_keyboard=admin_panel_button + view_orders_button + main_buttons)
        return markup
    if user.is_manager():
        markup = types.InlineKeyboardMarkup(inline_keyboard=view_orders_button + main_buttons)
        return markup

    markup = types.InlineKeyboardMarkup(inline_keyboard=main_buttons)
    return markup


# My Profile
def profile_markup(user: usr):
    profile_buttons = [
        [types.InlineKeyboardButton(text=tt.my_orders, callback_data="profile_orders")],
        [types.InlineKeyboardButton(text=tt.cancel_order, callback_data="profile_cancelOrder")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="profile_back")]
    ]

    markup = types.InlineKeyboardMarkup(inline_keyboard=profile_buttons)
    return markup


# Admin Panel
def admin_markup():
    admin_panel_buttons = [
        [types.InlineKeyboardButton(text=tt.item_management, callback_data="admin_itemManagement")],
        [types.InlineKeyboardButton(text=tt.user_management, callback_data="admin_userManagement")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="admin_back")]
    ]

    markup = types.InlineKeyboardMarkup(inline_keyboard=admin_panel_buttons)
    return markup


def user_management_markup(user: usr.User = None, back_button=False):
    if back_button or user.is_main_admin():
        user_management_buttons = [
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)

    elif user.is_admin():
        user_management_buttons = [
            [types.InlineKeyboardButton(text=tt.remove_admin, callback_data=f"um_removeAdmin_{user.get_id()}")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)

    elif user.is_manager():
        user_management_buttons = [
            [types.InlineKeyboardButton(text=tt.make_admin, callback_data=f"um_makeAdmin_{user.get_id()}")],
            [types.InlineKeyboardButton(text=tt.remove_manager, callback_data=f"um_removeManager_{user.get_id()}")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)

    else:
        user_management_buttons = [
            [types.InlineKeyboardButton(text=tt.make_admin, callback_data=f"um_makeAdmin_{user.get_id()}")],
            [types.InlineKeyboardButton(text=tt.make_manager, callback_data=f"um_makeManager_{user.get_id()}")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)

    return markup
