import sqlite3

from configuration import Configuration
import item as itm
import order as ordr

connection = sqlite3.connect('data.db')
cursor = connection.cursor()
config = Configuration()


class User:
    def __init__(self, user_id, username=None):
        self.__user_id = user_id

        if not user_exist(self.__user_id):
            cursor.execute(
                f"INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                [self.get_id(), username, 1 if str(self.get_id()) == config.get_main_admin_id() else 0, 0, "None"]
            )
            connection.commit()

    def get_id(self):
        return self.__user_id

    def __clist(self):
        cursor.execute("SELECT * FROM users WHERE user_id=?", [self.get_id()])
        return list(cursor)[0]

    def get_username(self):
        return self.__clist()[1]

    def get_cart_comma(self):
        return self.__clist()[4]

    def get_cart(self):
        cart = self.get_cart_comma()
        return [] if cart == "None" else list(map(itm.Item, cart.split(",")))

    def get_cart_price(self):
        item_list = self.get_cart_comma().split(',')
        set_of_items = set()
        for i in item_list:
            if int(i) not in set_of_items:
                set_of_items.add(int(i))
                price = 0
                for j in item_list:
                    if int(i) == int(j):
                        price += itm.Item(int(i)).get_price()
        return price

    def get_orders(self):
        cursor.execute("SELECT * FROM orders WHERE user_id=?", [self.get_id()])
        return list(map(ordr.Order, [order[0] for order in list(cursor)]))[::-1]

    def is_main_admin(self):
        return str(self.__user_id) == str(config.get_main_admin_id())

    def is_admin(self):
        return self.__clist()[2] == 1

    def set_admin(self, value):
        cursor.execute("UPDATE users SET is_admin=? WHERE user_id=?", [value, self.get_id()])
        connection.commit()

    def is_manager(self):
        return self.__clist()[3] == 1

    def set_manager(self, value):
        cursor.execute("UPDATE users SET is_manager=? WHERE user_id=?", [value, self.get_id()])
        connection.commit()

    def remove_from_cart(self, item_id):
        cart = [item.get_id() for item in self.get_cart()]
        cart.remove(str(item_id))
        cursor.execute(f"UPDATE users SET cart=? WHERE user_id=?", [",".join(cart) if cart else "None", self.get_id()])
        connection.commit()

    def add_to_cart(self, item_id, amount):
        for i in range(int(amount)):
            cart = self.get_cart()
            cursor.execute(
                f"UPDATE users SET cart=? WHERE user_id=?",
                [",".join([str(item.get_id()) for item in cart + [itm.Item(item_id)]]) if cart else str(item_id),
                 self.get_id()]
                )
            connection.commit()


def user_exist(user_id) -> bool:
    cursor.execute("SELECT * FROM users WHERE user_id=?", [user_id])
    return len(list(cursor)) != 0
