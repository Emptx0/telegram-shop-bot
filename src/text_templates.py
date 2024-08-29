import item as itm
import user as usr
import order as ordr


# Main menu
myGitHub = "<i>⭐️ My GitHub: https://github.com/Emptx0</i>"
greeting = "<b>Welcome to telegram shop bot!</b>"

admin_panel = "🅰️ Admin Panel"
view_orders = "📂 View Orders"
catalogue = "🗄️ Catalogue"
profile = "👤 Profile"
cart = "🛒 Cart"

back = "⬅️ Back"

# Admin panel
item_management = "📦 Item Management"
user_management = "🧍 User Management"

# Item management
select_cat = "📂 Select Category"
create_cat: list = ["➕ Create New Category", "✅ Category has been created successfully!"]
rename_cat: list = ["✏️ Rename Category", "✅ Category has been renamed successfully!"]
delete_cat: list = ["🗑️ Delete Category", "✅ Category has been deleted successfully!"]
get_cat_list = "📄 Categories List"

get_item_list = "📄 Items List"
manage_items = "📝 Manage Items"
add_item: list = ["➕ Add Item", "✅ Item has been added successfully!"]


def cat_info(cat_id, cat_name) -> str:
    msg_text = (f"Category ID: <b>{cat_id}</b>\n"
                f"Category name: {cat_name}")
    return msg_text


def get_cats(cat_list: list) -> str:
    msg_text = (f"{get_cat_list}:\n\n"
                f"<b>ID : Name</b>\n")
    for cat_id, cat_name in cat_list:
        msg_text += f"{cat_id} : {cat_name}\n"
    msg_text += "\nEnter ID of the category you want to manage:"
    return msg_text


rename_item: list = ["✏️ Rename Item", "✅ Name has been changed successfully!"]
change_price: list = ["💵 Change Price", "✅ Price has been changed successfully!"]
change_desc: list = ["📝 Change Description", "✅ Description has been changed successfully!"]
change_amount: list = ["✖️ Change Amount", "✅ Amount has been changed successfully!"]
upload_image: list = ["⬆️ Upload New Image", "✅ Image has been uploaded successfully!"]
delete_image: list = ["🗑️ Delete Image", "✅ Image has been deleted successfully!"]
delete_item: list = ["🗑️ Delete Item", "✅ Item has been deleted successfully!"]


def item_info(selected_item: itm.Item) -> str:
    msg_text = (f"ID - <b>{selected_item.get_id()}</b>\n"
                f"Name - {selected_item.get_name()}\n"
                f"Price - {selected_item.get_price()}\n"
                f"Amount - {selected_item.get_amount()}\n"
                f"Description: {selected_item.get_desc()}\n")
    return msg_text


def get_items(item_list: list) -> str:
    msg_text = (f"{get_item_list}:\n\n"
                f"<b>ID : Name</b>\n")
    for item_id, item_name in item_list:
        msg_text += f"{item_id} : {item_name}\n"
    msg_text += "\nEnter ID of the item you want to manage:"
    return msg_text


# User management
get_admin_list = "🔴 Admins list"
get_manager_list = "🔵 Managers list"

make_admin = "🔴 Give Admin Role"
make_manager = "🔵 Give Manager Role"

remove_admin = "🔴 Remove Admin Role"
remove_manager = "🔵 Remove Manager Role"


def get_users(user_list: list) -> str:
    msg_text = f"\n\n<b>ID : Username</b>\n"
    for user_id, username in user_list:
        msg_text += f"{user_id} : @{username}\n"
    msg_text += "\nEnter user ID you want to manage:"
    return msg_text


def user_info(user: usr.User) -> str:
    msg_text = (f"User ID - <b>{user.get_id()}</b>\n"
                f"Username - @{user.get_username()}\n"
                f"Status - %s" % ("Main Admin" if user.is_main_admin() else
                                  "Admin" if user.is_admin() else
                                  "Manager" if user.is_manager() else "Customer"))
    return msg_text


# View Item
add_to_cart: list = ["🛒 Add To Cart", "✅ Item has been added to cart!"]


def item(selected_item: itm.Item) -> str:
    msg_text = (f"Name - <b>{selected_item.get_name()}</b>\n"
                f"Price - ${selected_item.get_price()}\n"
                f"Amount - {selected_item.get_amount()}\n"
                f"Description: {selected_item.get_desc()}\n")
    return msg_text


# Profile
my_orders = "📂 My Orders"
cancel_order: list = ["❌ Cancel Order", "✅ Order has been canceled!"]


def profile_info(user_first_name, user: usr.User) -> str:
    msg_text = (f"Hi, <b>{user_first_name}</b>!\n"
                f"Status: %s" % ("Main Admin" if user.is_main_admin() else
                                 "Admin" if user.is_admin() else
                                 "Manager" if user.is_manager() else "Customer"))
    return msg_text


# Order
set_status_processing = "🔄 Set processing status"
set_status_delivered = "📦 Set delivered status"
set_status_done = "✅ Set done status"
set_status_canceled = "❌ Set canceled status"


def order_info(order: ordr.Order) -> str:
    msg_text = (f"ID - <b>{order.get_id()}</b>\n"
                f"Date - {order.get_date()}\n"
                f"Status - {order.get_status_string()}\n"
                f"Email address - {order.get_email_address()}\n"
                f"Home address - {order.get_home_address()}\n\n"
                f"Items:\n"
                f"{order.get_items_string()}\n\n"
                f"Price - <b>{order.get_price()}</b>")

    return msg_text


# Cart
cart_make_order: list = ["📦 Make Order", "✅ Order has been placed!"]
cart_remove_item: list = ["❌ Remove Item", "✅ Item has been removed!"]
select_currency = "💵 Select currency:"
complete_payment = "⬇️ Complete payment"
buy = "💰 Buy"
check = "✅ Check"


def cart_item_info(selected_item: itm.Item, amount) -> str:
    price = selected_item.get_price() * int(amount)
    msg_text = (f"Name - <b>{selected_item.get_name()}</b>\n"
                f"Price for <i>{amount}</i> - <b>${price}</b>\n"
                f"Description: {selected_item.get_desc()}\n")
    return msg_text
