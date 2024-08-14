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

    def get_name(self):
        return self.__clist()[1]

    def set_name(self, value):
        cursor.execute(f"UPDATE items SET name=? WHERE id=?", [value, self.get_id()])
        connection.commit()

    def get_price(self):
        return self.__clist()[2]

    def set_price(self, value):
        cursor.execute(f"UPDATE items SET price=? WHERE id=?", [value, self.get_id()])
        connection.commit()

    def get_cat(self):
        return self.__clist()[3]

    def set_cat(self, value):
        cursor.execute(f"UPDATE items SET cat_id=? WHERE id=?", [value, self.get_id()])
        connection.commit()

    def get_desc(self):
        return self.__clist()[4]

    def set_desc(self, value):
        cursor.execute(f"UPDATE items SET desc=? WHERE id=?", [value, self.get_id()])
        connection.commit()

    def get_amount(self):
        return self.__clist()[5]

    def set_amount(self, value):
        cursor.execute(f"UPDATE items SET amount=? WHERE id=?", [value, self.get_id()])
        connection.commit()

    def get_image_id(self):
        return self.__clist()[6]

    def get_image(self):
        return open("images/" + self.get_image_id(), "rb")

    def set_image_id(self, value):
        cursor.execute(f"UPDATE items SET image_id=? WHERE id=?", [value, self.get_id()])

    def delete(self):
        cursor.execute(f"DELETE FROM items WHERE id=?", [self.get_id()])
        connection.commit()


def item_exist(item_id):
    cursor.execute(f"SELECT * FROM items WHERE id=?", [item_id])
    return len(list(cursor)) == 1


def get_items_list(cat_id):
    cursor.execute("SELECT * FROM items WHERE cat_id=?", [cat_id])
    return list(map(Item, [item[0] for item in list(cursor)]))


def create_item(item_id, name, price, cat_id):
    cursor.execute(f"INSERT INTO items(id, name, price, cat_id, desc, amount, image_id) VALUES(?, ?, ?, ?, ?, ?, ?)",
                   [item_id, name, price, cat_id, "None", 0, 0]
                   )
    connection.commit()
