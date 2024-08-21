from aiogram import types
from collections import deque

import text_templates as tt
import user as usr
import category


# Main Menu
def main_menu_markup(user: usr):
    menu_buttons = [
        [types.InlineKeyboardButton(text=tt.catalogue, callback_data="main_catalogue")],
        [types.InlineKeyboardButton(text=tt.profile, callback_data="main_profile")],
        [types.InlineKeyboardButton(text=tt.cart, callback_data="main_cart")]
    ]
    admin_panel_button = [[types.InlineKeyboardButton(text=tt.admin_panel, callback_data="main_adminPanel")]]
    view_orders_button = [[types.InlineKeyboardButton(text=tt.view_orders, callback_data="main_viewOrders")]]

    if user.is_admin():
        markup = types.InlineKeyboardMarkup(inline_keyboard=admin_panel_button + view_orders_button + menu_buttons)
        return markup
    if user.is_manager():
        markup = types.InlineKeyboardMarkup(inline_keyboard=view_orders_button + menu_buttons)
        return markup

    markup = types.InlineKeyboardMarkup(inline_keyboard=menu_buttons)
    return markup


# Catalogue
def catalogue_cats_markup(cats_list):
    catalogue_buttons = list()

    for cat_id, cat_name in cats_list:
        catalogue_buttons.append([types.InlineKeyboardButton(text=cat_name, callback_data=f"cat_viewCat_{cat_id}")])
    catalogue_buttons.append([types.InlineKeyboardButton(text=tt.back, callback_data="cat_back")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=catalogue_buttons)
    return markup


def catalogue_items_markup(items_list):
    category_buttons = list()

    for item_id, item_name, item_price in items_list:
        category_buttons.append([
            types.InlineKeyboardButton(
                text=f"{item_name} - ${item_price}",
                callback_data=f"cat_viewItem_{item_id}"
            )
        ])
    category_buttons.append([types.InlineKeyboardButton(text=tt.back, callback_data=f"main_catalogue")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=category_buttons)
    return markup


def item_markup(item_id, cat_id):
    item_buttons = [
        [types.InlineKeyboardButton(text=tt.add_to_cart, callback_data=f"cat_addToCart_{item_id}")],
        [types.InlineKeyboardButton(text=tt.back, callback_data=f"cat_viewCat_{cat_id}")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=item_buttons)
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


def item_management_panel_markup(back=False):
    if not back:
        item_management_buttons = [
            [types.InlineKeyboardButton(text=tt.select_cat, callback_data="im_selectCat")],
            [types.InlineKeyboardButton(text=tt.create_cat[0], callback_data="im_createCat")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=item_management_buttons)
        return markup
    else:
        back_button = [
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
        return markup


def select_item_markup(cat_id, back=False):
    if not back:
        select_item_buttons = [
            [types.InlineKeyboardButton(text=tt.get_items_list, callback_data=f"im_getItems_{cat_id}")],
            [types.InlineKeyboardButton(text=tt.back, callback_data=f"im_backToCat_{cat_id}")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=select_item_buttons)
        return markup
    else:
        back_button = [
            [types.InlineKeyboardButton(text=tt.back, callback_data=f"im_backToCat_{cat_id}")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
        return markup


def select_cat_markup():
    select_cat_buttons = [
        [types.InlineKeyboardButton(text=tt.get_cats_list, callback_data="im_getCats")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=select_cat_buttons)
    return markup


def cat_management_markup(cat_id):
    cat_management_buttons = [
        [types.InlineKeyboardButton(text=tt.manage_items, callback_data=f"im_manageItems_{cat_id}")],
        [types.InlineKeyboardButton(text=tt.add_item[0], callback_data=f"im_addItem_{cat_id}")],
        [types.InlineKeyboardButton(text=tt.rename_cat[0], callback_data=f"im_renameCat_{cat_id}")],
        [types.InlineKeyboardButton(text=tt.delete_cat[0], callback_data=f"im_deleteCat_{cat_id}")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="im_back")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=cat_management_buttons)
    return markup


def cat_management_back():
    back_button = [
        [types.InlineKeyboardButton(text=tt.back, callback_data="im_back")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
    return markup


def item_management_markup(item_id, cat_id, back=False):
    item_management_buttons = [
        [types.InlineKeyboardButton(text=tt.rename_item[0], callback_data=f"im_renameItem_{item_id}")],
        [types.InlineKeyboardButton(text=tt.change_price[0], callback_data=f"im_changePrice_{item_id}")],
        [types.InlineKeyboardButton(text=tt.change_desc[0], callback_data=f"im_changeDesc_{item_id}")],
        [types.InlineKeyboardButton(text=tt.change_amount[0], callback_data=f"im_changeAmount_{item_id}")],
        [types.InlineKeyboardButton(text=tt.upload_image[0], callback_data=f"im_uploadImg_{item_id}")],
        [types.InlineKeyboardButton(text=tt.delete_image[0], callback_data=f"im_deleteImg_{item_id}")],
        [types.InlineKeyboardButton(text=tt.delete_item[0], callback_data=f"im_deleteItem_{item_id}")],
        [types.InlineKeyboardButton(text=tt.back, callback_data=f"im_backToCat_{cat_id}")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=item_management_buttons)
    return markup


def item_management_back(item_id):
    back_button = [
        [types.InlineKeyboardButton(text=tt.back, callback_data=f"im_backToItem_{item_id}")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
    return markup


def select_user_markup(user: usr.User):
    if user.is_main_admin():
        select_user_buttons = [
            [types.InlineKeyboardButton(text=tt.get_admins_list, callback_data="um_getAdmins")],
            [types.InlineKeyboardButton(text=tt.get_managers_list, callback_data="um_getManagers")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=select_user_buttons)
        return markup

    elif user.is_admin():
        select_user_buttons = [
            [types.InlineKeyboardButton(text=tt.get_managers_list, callback_data="um_getManagers")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=select_user_buttons)
        return markup


def user_management_markup(user: usr.User, main_admin_access):
    if main_admin_access:
        if user.is_main_admin():
            user_management_buttons = [
                [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
            ]
            markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)
            return markup

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

    else:
        if user.is_admin():
            user_management_buttons = [
                [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
            ]
            markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)

        elif user.is_manager():
            user_management_buttons = [
                [types.InlineKeyboardButton(text=tt.remove_manager, callback_data=f"um_removeManager_{user.get_id()}")],
                [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
            ]
            markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)

        else:
            user_management_buttons = [
                [types.InlineKeyboardButton(text=tt.make_manager, callback_data=f"um_makeManager_{user.get_id()}")],
                [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
            ]
            markup = types.InlineKeyboardMarkup(inline_keyboard=user_management_buttons)

        return markup


# Profile
def profile_markup(user: usr):
    profile_buttons = [
        [types.InlineKeyboardButton(text=tt.my_orders, callback_data="profile_orders")],
        [types.InlineKeyboardButton(text=tt.cancel_order, callback_data="profile_cancelOrder")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="profile_back")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=profile_buttons)
    return markup
