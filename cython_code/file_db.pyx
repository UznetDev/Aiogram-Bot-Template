# file_db.pyx
import json
import logging
import os
from cython cimport bint, dict

cdef class BotDb:
    cdef str file
    cdef dict json_data

    def __cinit__(self, str file):
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
            logging.info(f'Created new file: {file} with default data')

    def reading_db(self):
        with open(self.file, "r") as json_file:
            return json.load(json_file)

    def change_data(self, bint join_channel):
        self.json_data['join_channel'] = join_channel
        with open(self.file, "w") as json_file:
            json.dump(self.json_data, json_file)

cdef class FileDB:
    cdef str file
    cdef dict json_data

    def __cinit__(self, str file):
        self.file = file
        try:
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"ads": False,
                    "join_channel": False}
            with open(self.file, "w") as json_file:
                json.dump(data, json_file)
                os.chmod(self.file, 0o777)
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
            logging.info(f'Created new file: {file} with default data')

    def reading_db(self):
        try:
            with open(self.file, "r") as json_file:
                return json.load(json_file)
        except Exception as err:
            logging.info(f'Error reading the file: {err}')

    def add_data(self, data, str key):
        try:
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
                self.json_data[str(key)] = data
                with open(self.file, "w") as json_file:
                    json.dump(self.json_data, json_file)
        except Exception as err:
            logging.error(f'Error updating the file: {err}')

    def new_data(self, dict data):
        try:
            with open(self.file, "w") as json_file:
                json.dump(data, json_file)
        except Exception as err:
            logging.error(f'Error writing to the file: {err}')
