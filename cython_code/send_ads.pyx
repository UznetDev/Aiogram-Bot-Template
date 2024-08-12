# send_ads.pyx
import requests
import logging
import time
import mysql.connector  # Import normally, do not use 'cimport'
from data.config import *
from loader import db, file_db

cdef class MyDatabase:
    cdef str host, user, password, database
    cdef object connection  # Use 'object' since it's a generic Python object
    cdef object cursor      # Use 'object' since it's a generic Python object

    def __init__(self, str host, str user, str password, str database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.reconnect()

    def reconnect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_users_by_id(self, int start_id, int end_id) -> list:
        try:
            sql_query = "SELECT * FROM `users` WHERE `id` >= %s AND `id` < %s;"
            query_values = (start_id, end_id)
            self.cursor.execute(sql_query, query_values)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

cdef MyDatabase my_db = MyDatabase(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)

def copy_message_sync(int chat_id, int from_chat_id, int message_id, **kwargs):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/copyMessage"
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    data.update(kwargs)
    response = requests.post(url, data=data)
    return response.json()

def send_message_sync(int chat_id, str text, **kwargs):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    data.update(kwargs)
    response = requests.post(url, data=data)
    return response.json()

def send_ads():
    cdef float start_time, end_time, total_time, per_time
    cdef int start_index, end_index, total_users, chat_id, from_chat_id, message_id
    cdef str caption
    users_batch = None
    reply_markup = None

    try:
        start_time = time.time()
        ads_data = file_db.reading_db()['ads']
        if ads_data:
            start_index = ads_data['start']
            from_chat_id = ads_data['from_chat_id']
            message_id = ads_data['message_id']
            caption = ads_data['caption']
            reply_markup = ads_data['reply_markup']
            total_users = ads_data['total_users']
            end_index = min(start_index + 100, total_users)

            users_batch = my_db.select_users_by_id(start_index, end_index)
            if users_batch:
                logging.info(f'Sending ads to users {start_index} - {end_index} (Total: {len(users_batch)})')
                for user in users_batch:
                    try:
                        chat_id = user[1]
                        copy_message_sync(chat_id,
                                          from_chat_id,
                                          message_id,
                                          caption=caption,
                                          reply_markup=reply_markup)
                        ads_data["done_count"] += 1
                    except Exception as err:
                        logging.error(err)
                        ads_data["fail_count"] += 1

                if end_index < total_users:
                    time.sleep(1)
                    end_time = time.time()
                    total_time = end_time - start_time
                    per_time = ads_data["per_time"]
                    if per_time < total_time:
                        ads_data["per_time"] = per_time
                    ads_data['start'] = end_index
                    file_db.add_data(ads_data, key='ads')
                    return send_ads()
                else:
                    file_db.add_data(False, key='ads')
                    summary_message = (
                        f"📬 Advertisement Sending Completed\n\n"
                        f"👥 Total Users: {total_users}\n"
                        f"✅  Sent: {ads_data['done_count']}\n"
                        f"❌  Failed: {ads_data['fail_count']}\n"
                        f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                        f"🕒 End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                    )
                    send_message_sync(from_chat_id, summary_message)
            elif users_batch is None:
                db.reconnect()
                time.sleep(2)
            else:
                return
        else:
            return
    except Exception as err:
        logging.error(err)
