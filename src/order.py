import sqlite3
from datetime import datetime

from configuration import Configuration
import item as itm

connection = sqlite3.connect('data.db')
cursor = connection.cursor()
config = Configuration()


class Order:
    def __init__(self, order_id):
        self.__order_id = order_id

    def get_id(self):
        return self.__order_id

    def __clist(self):
        cursor.execute(f"SELECT * FROM orders WHERE order_id=?", [self.get_id()])
        return list(cursor)[0]

    def get_user_id(self):
        return self.__clist()[1]

    def get_item_list_comma(self):
        return self.__clist()[2]

    def get_items_string(self):
        item_list = self.get_item_list_comma().split(',')
        set_of_items = set()
        order_list = ""
        for i in item_list:
            if int(i) not in set_of_items:
                set_of_items.add(int(i))
                amount = 0
                for j in item_list:
                    if int(i) == int(j):
                        amount += 1
                order_list += f"{itm.Item(int(i)).get_name()} - {amount}\n"
        return order_list

    def get_price(self):
        item_list = self.get_item_list_comma().split(',')
        set_of_items = set()
        for i in item_list:
            if int(i) not in set_of_items:
                set_of_items.add(int(i))
                price = 0
                for j in item_list:
                    if int(i) == int(j):
                        price += itm.Item(int(i)).get_price()
        return price

    def get_email_address(self):
        return self.__clist()[3]

    def get_home_address(self):
        return self.__clist()[4]

    def get_date(self):
        return self.__clist()[5]

    def get_status(self):
        return self.__clist()[6]

    def get_status_string(self):
        return get_status_dict()[self.__clist()[6]]

    def set_status(self, value):
        cursor.execute(f"UPDATE orders SET status=? WHERE order_id=?", (value, self.get_id()))
        connection.commit()


def get_status_dict():
    return {
        0: "In process",
        1: "Delivered",
        2: "Done",
        -1: "Canceled"
    }


def order_exists(order_id) -> bool:
    cursor.execute("SELECT * FROM orders WHERE user_id=?", [order_id])
    return len(list(cursor)) != 0


def create_order(order_id, user_id, item_list, email_address, home_address):
    cursor.execute(
        f"INSERT INTO orders VALUES(?, ?, ?, ?, ?, ?, ?)",
        [order_id, user_id, item_list, email_address, home_address, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0]
    )
    connection.commit()
