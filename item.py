import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()


class Item:
    def __init__(self, item_id):
        self.__item_id = item_id

    def __clist(self):
        cursor.execute(f"SELECT * FROM items WHERE id=?", [self.get_id()])
        return list(cursor)[0]

    def get_id(self):
        return self.__item_id


def get_item_list():
    cursor.execute("SELECT * FROM items")
    return list(map(Item, [item[0] for item in list(cursor)]))


def create_item(name, price, cat_id, desc, amount, image_id):
    cursor.execute(f"INSERT INTO items VALUES(?, ?, ?, ?, ?, ?)",
                   [name, price, cat_id, desc, amount, image_id]
                   )
