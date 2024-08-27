from os import remove, mkdir, rmdir, listdir
from os.path import exists

import sqlite3


def create_config(token, main_admin_id, config_path="config.ini"):
    DEFAULT_CONFIG_TEXT = f"""[settings]
token = {token}
main_admin_id = {main_admin_id}
"""
    with open(config_path, "w") as config:
        config.write(DEFAULT_CONFIG_TEXT)


CREATE_USERS_TEXT = """
        CREATE TABLE "users" (
            "user_id" INTEGER NOT NULL,
            "username" TEXT NOT NULL,
            "is_admin" INTEGER,
            "is_manager" INTEGER,
            "cart" TEXT
)
"""


CREATE_CATS_TEXT = """
    CREATE TABLE "categories" (
        "id" INTEGER,
        "name" TEXT NOT NULL,
        PRIMARY KEY("id")
    )
"""


CREATE_ITEMS_TEXT = """
        CREATE TABLE "items" (
            "id" INTEGER,
            "name" TEXT NOT NULL,
            "price" FLOAT NOT NULL,
            "cat_id" INTEGER NOT NULL,
            "desc" TEXT,
            "amount" INTEGER,
            "image_id" INTEGER,
            PRIMARY KEY("id")
        )
"""


CREATE_ORDERS_TEXT = """
    CREATE TABLE "orders" (
        "order_id" INTEGER,
        "user_id" INTEGER,
        "item_list" TEXT,
        "email_address" TEXT,
        "home_address" TEXT,
        "date" TEXT,
        "status" INTEGER
    )
"""


def create_db():
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    cursor.execute(CREATE_USERS_TEXT)
    cursor.execute(CREATE_CATS_TEXT)
    cursor.execute(CREATE_ITEMS_TEXT)
    cursor.execute(CREATE_ORDERS_TEXT)
    connection.commit()
    connection.close()


def files_exist():
    return any(list(map(exists, ["config.ini", "data.db"])))


if __name__ == "__main__":
    if files_exist():
        while True:
            conf = input(
                "Are you sure you want to restart the installation process? All data will be lost! (Y/N) "
            )
            if conf.lower() in ["y", "yes", "n", "no", ""]:
                break
    else:
        conf = "y"

    if conf.lower() in ["y", "yes"]:
        token = input("Enter bot token: ")
        main_admin_id = input("Enter main admin id: ")
        if main_admin_id.isalnum():
            if exists("data.db"):
                remove("data.db")
                print("Database has been deleted.")
            create_db()
            print("Database has been created.")

            if exists("config.ini"):
                remove("config.ini")
                print("Configuration file has been deleted.")
            create_config(token, main_admin_id)
            print("Configuration file has been created.")

            if exists("images"):
                for file in listdir("images"):
                    remove("images/" + file)
                rmdir("images")
                print('"images" folder has been deleted.')
            mkdir("images")
            print('"images" folder has been created.')
        else:
            print("Invalid user ID.")
    else:
        print("Installation was canceled.")
