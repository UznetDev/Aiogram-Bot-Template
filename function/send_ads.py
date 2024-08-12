# import requests
# import logging
# import time
# import mysql.connector
# from data.config import *
# from loader import db, file_db
#
#
# class MyDatabase:
#     def __init__(self, host, user, password, database):
#         """
#         Initialize the MyDatabase object with connection parameters.
#
#         Parameters:
#         host (str): The hostname of the MySQL server.
#         user (str): The username to connect to the MySQL server.
#         password (str): The password to connect to the MySQL server.
#         database (str): The name of the database to connect to.
#         """
#         self.host = host
#         self.user = user
#         self.password = password
#         self.database = database
#         self.reconnect()
#
#     def reconnect(self):
#         """
#         Reconnect to the MySQL database. If the connection fails, log the error and attempt to reconnect.
#         """
#         try:
#             self.connection = mysql.connector.connect(
#                 host=self.host,
#                 user=self.user,
#                 password=self.password,
#                 database=self.database,
#                 autocommit=True
#             )
#             self.cursor = self.connection.cursor()
#         except mysql.connector.Error as err:
#             logging.error(err)
#             self.reconnect()
#         except Exception as err:
#             logging.error(err)
#
#     def select_users_by_id(self, start_id: int, end_id: int) -> list:
#         """
#         Select users from the 'users' table by their ID.
#
#         :param start_id: The starting ID (inclusive).
#         :param end_id: The ending ID (exclusive).
#
#         :return list: A list of tuples containing user data.
#         """
#         try:
#             sql_query = "SELECT * FROM `users` WHERE `id` >= %s AND `id` < %s;"
#             query_values = (start_id, end_id)
#             self.cursor.execute(sql_query, query_values)
#             result = self.cursor.fetchall()
#             return result
#         except mysql.connector.Error as err:
#             logging.error(err)
#             self.reconnect()
#         except Exception as err:
#             logging.error(err)
#
#
# my_db = MyDatabase(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
#
#
# def copy_message_sync(chat_id, from_chat_id, message_id, **kwargs):
#     """
#     Synchronously copy a message from one chat to another using the Telegram API.
#
#     :param chat_id: The target chat ID where the message will be copied.
#     :param from_chat_id: The chat ID where the message originates.
#     :param message_id: The ID of the message to copy.
#     :param kwargs: Additional optional parameters for the API request.
#
#     :return dict: The JSON response from the Telegram API.
#     """
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/copyMessage"
#     data = {
#         "chat_id": chat_id,
#         "from_chat_id": from_chat_id,
#         "message_id": message_id
#     }
#     data.update(kwargs)
#     response = requests.post(url, data=data)
#     return response.json()
#
# def send_message_sync(chat_id, text, **kwargs):
#     """
#     Synchronously send a message to a specific chat using the Telegram API.
#
#     :param chat_id: The target chat ID where the message will be sent.
#     :param text: The text of the message to send.
#     :param kwargs: Additional optional parameters for the API request.
#
#     :return dict: The JSON response from the Telegram API.
#     """
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     data = {
#         "chat_id": chat_id,
#         "text": text
#     }
#     data.update(kwargs)
#     response = requests.post(url, data=data)
#     return response.json()
#
#
# def send_ads():
#     """
#     Function to handle the advertisement sending process.
#
#     This function reads the advertisement data from the database, selects a batch of users,
#     and sends the advertisement message to each user. It updates the advertisement progress
#     and logs any errors that occur. If the entire batch of users is processed, it terminates
#     the sending process and updates the status in the database.
#     """
#     try:
#         start_time = time.time()
#         ads_data = file_db.reading_db()['ads']
#         if ads_data:
#             start_index = ads_data['start']
#             from_chat_id = ads_data['from_chat_id']
#             message_id = ads_data['message_id']
#             caption = ads_data['caption']
#             reply_markup = ads_data['reply_markup']
#             total_users = ads_data['total_users']
#             end_index = min(start_index + 100, total_users)
#
#             users_batch = my_db.select_users_by_id(start_index, end_index)
#             if users_batch:
#                 logging.info(f'Sending ads to users {start_index} - {end_index} (Total: {len(users_batch)})')
#                 for user in users_batch:
#                     try:
#                         chat_id = user[1]
#                         copy_message_sync(chat_id,
#                                           from_chat_id,
#                                           message_id,
#                                           caption=caption,
#                                           reply_markup=reply_markup)
#                         ads_data["done_count"] += 1
#                     except Exception as err:
#                         logging.error(err)
#                         ads_data["fail_count"] += 1
#
#                 if end_index < total_users:
#                     time.sleep(1)
#                     end_time = time.time()
#                     total_time = end_time - start_time
#                     per_time = ads_data["per_time"]
#                     if per_time< total_time:
#                         ads_data["per_time"] = per_time
#                     ads_data['start'] = end_index
#                     file_db.add_data(ads_data, key='ads')
#                     return send_ads()  # Recursive call to continue sending to the next batch
#                 else:
#                     file_db.add_data(False, key='ads')
#                     summary_message = (
#                         f"📬 Advertisement Sending Completed\n\n"
#                         f"👥 Total Users: {total_users}\n"
#                         f"✅  Sent: {ads_data['done_count']}\n"
#                         f"❌  Failed: {ads_data['fail_count']}\n"
#                         f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
#                         f"🕒 End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
#                     )
#                     send_message_sync(from_chat_id, summary_message)
#             elif users_batch is None:
#                 db.reconnect()
#                 time.sleep(2)
#             else:
#                 return
#         else:
#             return
#     except Exception as err:
#         logging.error(err)