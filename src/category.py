import sqlite3

import item as itm

connection = sqlite3.connect('data.db')
cursor = connection.cursor()


class Category:
    def __init__(self, cat_id):
        self.__id = cat_id

    def __clist(self):
        cursor.execute(f"SELECT * FROM categories WHERE id = ?", [self.get_id()])
        return list(cursor)[0]

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__clist()[1]

    def set_name(self, value):
        cursor.execute(f"UPDATE categories SET name = ? WHERE id = ?", [value, self.get_id()])
        connection.commit()

    def delete(self):
        cursor.execute(f"DELETE FROM categories WHERE id = ?", [self.get_id()])
        connection.commit()


def category_exist(cat_id):
    cursor.execute(f"SELECT * FROM categories WHERE id=?", [cat_id])
    return len(list(cursor)) == 1


def create_cat(cat_id, cat_name):
    cursor.execute(f"INSERT INTO categories (id, name) VALUES (?, ?)", [cat_id, cat_name])
    connection.commit()


if __name__ == '__main__':
    cat = Category(431)
    cat.set_name("aasdasd")
