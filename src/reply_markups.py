import re

from aiogram import types

import text_templates as tt
import user as usr


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
def catalogue_cats_markup(cat_list):
    catalogue_buttons = list()

    for cat_id, cat_name in cat_list:
        catalogue_buttons.append([types.InlineKeyboardButton(text=cat_name, callback_data=f"cat_viewCat_{cat_id}")])
    catalogue_buttons.append([types.InlineKeyboardButton(text=tt.back, callback_data="cat_back")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=catalogue_buttons)
    return markup


def catalogue_items_markup(item_list):
    category_buttons = list()

    for item_id, item_name, item_price in item_list:
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
        [types.InlineKeyboardButton(text=tt.add_to_cart[0], callback_data=f"cat_addToCart_{item_id}")],
        [types.InlineKeyboardButton(text=tt.back, callback_data=f"cat_viewCat_{cat_id}")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=item_buttons)
    return markup


def back_to_item_markup(item_id):
    back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data=f"cat_viewItem_{item_id}")]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
    return markup


# View Orders Panel
def get_orders_markup(order_list):
    order_buttons = list()

    for order_id in order_list:
        order_buttons.append([
            types.InlineKeyboardButton(
                text=f"Order - {[*order_id][0]}",
                callback_data=f"management_viewOrder_{[*order_id][0]}"
            )
        ])
    order_buttons.append([types.InlineKeyboardButton(text=tt.back, callback_data="cat_back")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=order_buttons)
    return markup


def order_management_markup(order_id):
    order_buttons = [
        [types.InlineKeyboardButton(text=tt.set_status_processing, callback_data=f"management_processing_{order_id}")],
        [types.InlineKeyboardButton(text=tt.set_status_delivered, callback_data=f"management_delivered_{order_id}")],
        [types.InlineKeyboardButton(text=tt.set_status_done, callback_data=f"management_done_{order_id}")],
        [types.InlineKeyboardButton(text=tt.set_status_canceled, callback_data=f"management_canceled_{order_id}")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="cat_back")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=order_buttons)
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
        back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]]
        markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
        return markup


def select_item_markup(cat_id, back=False):
    if not back:
        select_item_buttons = [
            [types.InlineKeyboardButton(text=tt.get_item_list, callback_data=f"im_getItems_{cat_id}")],
            [types.InlineKeyboardButton(text=tt.back, callback_data=f"im_backToCat_{cat_id}")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=select_item_buttons)
        return markup
    else:
        back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data=f"im_backToCat_{cat_id}")]]
        markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
        return markup


def select_cat_markup():
    select_cat_buttons = [
        [types.InlineKeyboardButton(text=tt.get_cat_list, callback_data="im_getCats")],
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
    back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data="im_back")]]
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
    back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data=f"im_backToItem_{item_id}")]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
    return markup


def select_user_markup(user: usr.User):
    if user.is_main_admin():
        select_user_buttons = [
            [types.InlineKeyboardButton(text=tt.get_admin_list, callback_data="um_getAdmins")],
            [types.InlineKeyboardButton(text=tt.get_manager_list, callback_data="um_getManagers")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=select_user_buttons)
        return markup

    elif user.is_admin():
        select_user_buttons = [
            [types.InlineKeyboardButton(text=tt.get_manager_list, callback_data="um_getManagers")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=select_user_buttons)
        return markup


def user_management_markup(user: usr.User, main_admin_access):
    if main_admin_access:
        if user.is_main_admin():
            user_management_buttons = [[types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]]
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
            user_management_buttons = [[types.InlineKeyboardButton(text=tt.back, callback_data="um_back")]]
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
def profile_markup():
    profile_buttons = [
        [types.InlineKeyboardButton(text=tt.my_orders, callback_data="profile_orders")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="profile_back")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=profile_buttons)
    return markup


def get_user_orders_markup(order_list):
    order_buttons = list()
    for order in order_list:
        order_buttons.append([
            types.InlineKeyboardButton(
                text=f"Order - {order.get_id()}",
                callback_data=f"profile_viewOrder_{order.get_id()}"
            )
        ])
    order_buttons.append([types.InlineKeyboardButton(text=tt.back, callback_data="main_profile")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=order_buttons)
    return markup


def order_markup(order_id, order_status):
    if order_status != -1:
        orders_buttons = [
            [types.InlineKeyboardButton(text=tt.cancel_order[0], callback_data=f"profile_cancelOrder_{order_id}")],
            [types.InlineKeyboardButton(text=tt.back, callback_data="main_profile")]
        ]
    else:
        orders_buttons = [[types.InlineKeyboardButton(text=tt.back, callback_data="main_profile")]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=orders_buttons)
    return markup


def back_to_profile():
    back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data="main_profile")]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
    return markup


# Cart
def back_to_main_menu():
    back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data="cat_back")]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
    return markup


def get_cart_markup(cart_item_list):
    cart_buttons = list()
    set_of_items = set()
    for i in cart_item_list:
        if i.get_id() not in set_of_items:
            set_of_items.add(i.get_id())
            amount = 0
            for j in cart_item_list:
                if i.get_id() == j.get_id():
                    amount += 1
            cart_buttons.append([
                types.InlineKeyboardButton(
                    text=f"{i.get_name()} - {amount}",
                    callback_data=f"cart_viewItem_{i.get_id()}_{amount}"
                )
            ])
    cart_buttons.append([types.InlineKeyboardButton(text=tt.cart_make_order[0], callback_data=f"cart_makeOrder")])
    cart_buttons.append([types.InlineKeyboardButton(text=tt.back, callback_data=f"cart_back")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=cart_buttons)
    return markup


def cart_item_view_markup(item_id):
    buttons = [
        [types.InlineKeyboardButton(text=tt.cart_remove_item[0], callback_data=f"cart_removeItem_{item_id}")],
        [types.InlineKeyboardButton(text=tt.back, callback_data="cart_backToCart")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def back_to_cart():
    back_button = [[types.InlineKeyboardButton(text=tt.back, callback_data="cart_backToCart")]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=back_button)
    return markup
