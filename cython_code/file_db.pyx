# db.pyx
from libc.stdio cimport fopen, fclose, fread, fwrite
from libc.stdlib cimport malloc, free
from libc.string cimport strcpy, strlen
import json
import logging
import os
from cython cimport ctypedef

ctypedef struct {
    char* file
    dict json_data
} BotDb

ctypedef struct {
    char* file
    dict json_data
} FileDB

cdef class BotDb:
    def __cinit__(self, file: str):
        """
        Initializes the BotDb instance and loads data from the specified JSON file.

        Parameters:
        - file (str): The path to the JSON file to be used for storing data.
        """
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
        """
        Reads and returns the JSON data from the file.
        """
        with open(self.file, "r") as json_file:
            return json.load(json_file)

    def change_data(self, join_channel: bool):
        """
        Updates the 'join_channel' value in the JSON file.
        """
        self.json_data['join_channel'] = join_channel
        with open(self.file, "w") as json_file:
            json.dump(self.json_data, json_file)

cdef class FileDB:
    def __cinit__(self, file: str):
        """
        Initializes the FileDB instance and loads data from the specified JSON file.
        """
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
            logging.info(f'Created new file: {file} with default data')

    def reading_db(self):
        """
        Reads and returns the JSON data from the file.
        """
        try:
            with open(self.file, "r") as json_file:
                return json.load(json_file)
        except Exception as err:
            logging.info(f'Error reading the file: {err}')

    def add_data(self, data, key: str):
        """
        Adds or updates an entry in the JSON file with the given key and data.
        """
        try:
            with open(self.file, "r") as json_file:
                self.json_data = json.load(json_file)
                self.json_data[str(key)] = data
                with open(self.file, "w") as json_file:
                    json.dump(self.json_data, json_file)
        except Exception as err:
            logging.error(f'Error updating the file: {err}')

    def new_data(self, data: dict):
        """
        Replaces the entire JSON content of the file with new data.
        """
        try:
            with open(self.file, "w") as json_file:
                json.dump(data, json_file)
        except Exception as err:
            logging.error(f'Error writing to the file: {err}')
