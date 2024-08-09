# /start Main menu
greeting = "<b>Welcome to telegram test shop!</b>"

admin_panel = "🅰️ Admin Panel"
catalogue = "🗄️ Catalogue"
profile = "👤 My Profile"
cart = "🛒 Cart"

back = "⬅️ Back"

# Admin panel
item_management = "📦 Item Management"
user_management = "🧍 User Management"

# Admin panel/User management
get_admins_list = "🔴 Admins list"
get_managers_list = "🔵 Managers list"

make_admin = "🔴 Give Admin Role"
make_manager = "🔵 Give Manager Role"

remove_admin = "🔴 Remove Admin Role"
remove_manager = "🔵 Remove Manager Role"


def user_info(user_id, username, is_main_admin, is_admin, is_manager) -> str:
    msg_text = (f"User id: <b>{user_id}</b>\n"
                f"Username: @{username}\n"
                f"Status: %s" % ("Main Admin" if is_main_admin else
                                 "Admin" if is_admin else
                                 "Manager" if is_manager else "Customer"))
    return msg_text


# Manager panel
view_orders = "📂 View Orders"

# Profile
my_orders = "📂 My Orders"
cancel_order = "❌ Cancel Order"


def profile_info(user_first_name, is_main_admin, is_admin, is_manager):
    msg_text = (f"Hi, <b>{user_first_name}</b>!\n"
                f"Status: %s" % ("Main Admin" if is_main_admin else
                                 "Admin" if is_admin else
                                 "Manager" if is_manager else "Customer"))
    return msg_text
