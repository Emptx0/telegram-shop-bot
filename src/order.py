import sqlite3
from datetime import datetime

from configuration import Configuration
from item import Item

connection = sqlite3.connect('data.db')
cursor = connection.cursor()
config = Configuration()


class Order:
    def __init__(self, order_id):
        self.__order_id = order_id

    def get_id(self):
        return self.__order_id

    def __clist(self):
        cursor.execute(f"SELECT * FROM orders WHERE id=?", [self.get_id()])
        return list(cursor)[0]

    def get_user_id(self):
        return self.__clist()[1]

    def get_item_list_comma(self):
        return self.__clist()[2]

    def get_items(self):
        cart = self.get_item_list_comma()
        return list(map(Item, cart.split(",")))

    def get_status(self):
        return self.__clist()[6]

    def set_status(self, value):
        cursor.execute(f"UPDATE orders SET status=? WHERE id=?", (value, self.get_id()))


def order_exists(order_id) -> bool:
    cursor.execute("SELECT * FROM orders WHERE user_id=?", [order_id])
    return len(list(cursor)) != 0


def create_order(order_id, user_id, item_list, email_address, home_address):
    cursor.execute(
        f"INSERT INTO orders VALUES(?, ?, ?, ?, ?, ?, ?)",
        [order_id, user_id, item_list, email_address, home_address, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0]
    )
    connection.commit()
