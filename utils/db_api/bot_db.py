import json
import logging
import os


class BotDb:
    def __init__(self, file):
        self.file = file
        try:
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"join_channel": False}
            with open(self.file, "w") as json_file:
                json.dump(data, json_file)
                os.chmod(self.file, 0o777)
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
            logging.info(f' create table in file{file}')

    def reading_db(self):
        with open(self.file, "r") as json_file:
            return json.load(json_file)

    def change_data(self, join_channel):
        self.json_data['join_channel'] = join_channel
        with open(self.file, "w") as json_file:
            json.dump(self.json_data, json_file)


class MusicDB:
    def __init__(self, file: str):
        self.file = file
        try:
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
            with open(self.file, "w") as json_file:
                json.dump(data, json_file)
                os.chmod(self.file, 0o777)
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
            logging.info(f' create table in file{file}')

    def reading_db(self):
        try:
            with open(self.file, "r") as json_file:
                return json.load(json_file)
        except Exception as err:
            logging.info(err)

    def add_data(self, data, key: str):
        try:
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
                self.json_data[str(key)] = data
                with open(self.file, "w") as json_file:
                    json.dump(self.json_data, json_file)
        except Exception as err:
            logging.error(err)

    def new_data(self, data):
        try:
            with open(self.file, "w") as json_file:
                json.dump(data, json_file)
        except Exception as err:
            logging.error(err)
