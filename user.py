import sqlite3

from configuration import Configuration

connection = sqlite3.connect('data.db')
cursor = connection.cursor()
config = Configuration()


class User:
    def __init__(self, user_id):
        self.__user_id = user_id

        if not user_exists(self.__user_id):
            cursor.execute(
                f"INSERT INTO users VALUES (?, ?, ?, ?)",
                [self.get_id(), 1 if str(self.get_id()) == config.get_main_admin_id() else 0, 0, "None"]
            )
            connection.commit()

    def __user_list(self):
        cursor.execute("SELECT * FROM users WHERE user_id = ?", [self.get_id()])
        return list(cursor)[0]

    def get_id(self):
        return self.__user_id

    def is_admin(self):
        return self.__user_list()[1] == 1

    def set_admin(self, value):
        cursor.execute("UPDATE users SET is_admin=? WHERE user_id = ?", [value, self.get_id()])

    def is_manager(self):
        return self.__user_list()[2] == 1

    def set_manager(self, value):
        cursor.execute("UPDATE users SET is_manager=? WHERE user_id = ?", [value, self.get_id()])


def user_exists(user_id) -> bool:
    cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
    return len(cursor.fetchall()) != 0
