from configparser import ConfigParser
import sqlite3


class Configuration:
    def __init__(self, config_path="config.ini"):
        self.__config_path = config_path

    def __read_config(self):
        config = ConfigParser()
        config.read(self.__config_path)
        return config

    def __set_config(self, section, key, value):
        config = self.__read_config()
        config.set(section, key, str(value))
        with open(self.__config_path, "w") as configfile:
            config.write(configfile)

    def get_token(self):
        return self.__read_config()["settings"]["token"]

    def set_token(self, token):
        self.__set_config("settings", "token", token)

    def get_main_admin_id(self):
        return self.__read_config()["settings"]["main_admin_id"]

    def set_main_admin_id(self, main_admin_id):
        self.__set_config("settings", "main_admin_id", main_admin_id)
