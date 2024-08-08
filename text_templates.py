
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
get_manager_list = "🔵 Manager list"

make_admin = "🔴 Give Admin Role"
make_manager = "🔵 Give Manager Role"

remove_admin = "🔴 Remove Admin Role"
remove_manager = "🔵 Remove Manager Role"


def user_info(user_id, main_admin_id, is_admin, is_manager) -> str:
    msg_text = (f"User id: <b>{user_id}</b>\n"
                f"Status: %s" % ("Main Admin" if user_id == main_admin_id else
                                 "Admin" if is_admin else
                                 "Manager" if is_manager else "Customer"))
    return msg_text


# Manager panel
view_orders = "📂 View Orders"

# Profile
my_orders = "📂 My Orders"
cancel_order = "❌ Cancel Order"
