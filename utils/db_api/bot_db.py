# import json
# import logging
# import os
#
#
# class BotDb:
#     def __init__(self, file):
#         """
#         Initializes the BotDb instance and loads data from the specified JSON file.
#
#         Parameters:
#         - file (str): The path to the JSON file to be used for storing data.
#
#         This constructor attempts to load the JSON data from the file. If the file does not exist or
#         contains invalid JSON, it creates a new file with default data and sets file permissions to 0777.
#         """
#         self.file = file
#         try:
#             with open(self.file, "r") as json_file:
#                 self.json_data = json.load(json_file)
#         except (FileNotFoundError, json.JSONDecodeError):
#             data = {"join_channel": False}
#             with open(self.file, "w") as json_file:
#                 json.dump(data, json_file)
#                 os.chmod(self.file, 0o777)
#             with open(self.file, "r") as json_file:
#                 self.json_data = json.load(json_file)
#             logging.info(f'Created new file: {file} with default data')
#
#     def reading_db(self):
#         """
#         Reads and returns the JSON data from the file.
#
#         Parameters:
#         - None
#
#         Returns:
#         - dict: The JSON data loaded from the file.
#         """
#         with open(self.file, "r") as json_file:
#             return json.load(json_file)
#
#     def change_data(self, join_channel):
#         """
#         Updates the 'join_channel' value in the JSON file.
#
#         Parameters:
#         - join_channel (bool): The new value to set for 'join_channel'.
#
#         Returns:
#         - None
#         """
#         self.json_data['join_channel'] = join_channel
#         with open(self.file, "w") as json_file:
#             json.dump(self.json_data, json_file)
#
#
# class FileDB:
#     def __init__(self, file: str):
#         """
#         Initializes the FileDB instance and loads data from the specified JSON file.
#
#         Parameters:
#         - file (str): The path to the JSON file to be used for storing data.
#
#         This constructor attempts to load the JSON data from the file. If the file does not exist or
#         contains invalid JSON, it creates a new file with default empty data and sets file permissions to 0777.
#         """
#         self.file = file
#         try:
#             with open(self.file, "r") as json_file:
#                 self.json_data = json.load(json_file)
#         except (FileNotFoundError, json.JSONDecodeError):
#             data = {}
#             with open(self.file, "w") as json_file:
#                 json.dump(data, json_file)
#                 os.chmod(self.file, 0o777)
#             with open(self.file, "r") as json_file:
#                 self.json_data = json.load(json_file)
#             logging.info(f'Created new file: {file} with default data')
#
#     def reading_db(self):
#         """
#         Reads and returns the JSON data from the file.
#
#         Parameters:
#         - None
#
#         Returns:
#         - dict: The JSON data loaded from the file.
#         """
#         try:
#             with open(self.file, "r") as json_file:
#                 return json.load(json_file)
#         except Exception as err:
#             logging.info(f'Error reading the file: {err}')
#
#     def add_data(self, data, key: str):
#         """
#         Adds or updates an entry in the JSON file with the given key and data.
#
#         Parameters:
#         - data (any): The data to store in the JSON file.
#         - key (str): The key under which the data will be stored.
#
#         Returns:
#         - None
#         """
#         try:
#             with open(self.file, "r") as json_file:
#                 self.json_data = json.load(json_file)
#                 self.json_data[str(key)] = data
#                 with open(self.file, "w") as json_file:
#                     json.dump(self.json_data, json_file)
#         except Exception as err:
#             logging.error(f'Error updating the file: {err}')
#
#     def new_data(self, data):
#         """
#         Replaces the entire JSON content of the file with new data.
#
#         Parameters:
#         - data (dict): The new data to write to the file.
#
#         Returns:
#         - None
#         """
#         try:
#             with open(self.file, "w") as json_file:
#                 json.dump(data, json_file)
#         except Exception as err:
#             logging.error(f'Error writing to the file: {err}')
