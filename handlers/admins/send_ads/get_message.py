import requests
import asyncio
import logging
import time
import mysql.connector
from aiogram import types
from aiogram.fsm.context import FSMContext
from concurrent.futures import ProcessPoolExecutor
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from keyboards.inline.admin_btn import main_admin_panel_btn
from data.config import *
from keyboards.inline.close_btn import close_btn
from loader import dp, db, bot, file_db
from states.admin_state import AdminState


class MyDatabase:
    def __init__(self, host, user, password, database):
        """
        Initialize the Database object with connection parameters.

        Parameters:
        host (str): The hostname of the MySQL server.
        user (str): The username to connect to the MySQL server.
        password (str): The password to connect to the MySQL server.
        database (str): The name of the database to connect to.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.reconnect()

    def reconnect(self):
        """
        Reconnect to the MySQL database. If the connection fails, log the error and attempt to reconnect.
        """
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

    def select_users_by_id(self, start_id: int, end_id: int) -> list:
        """
        Select user from the 'users' table on id.

        :param start_id: The start ID (integer).
        :param end_id: The end ID (integer).

        :return list: A list of tuples containing all users.
        """
        try:
            sql = "SELECT * FROM `users` WHERE `id` >= %s AND `id` < %s;"
            value = (start_id, end_id)
            self.cursor.execute(sql, value)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


my_db = MyDatabase(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)


def copy_message_sync(chat_id, from_chat_id, message_id, **kwargs):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/copyMessage"
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    data.update(kwargs)

    response = requests.post(url, data=data)
    return response.json()

def send_message_sync(chat_id, text, **kwargs):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    data.update(kwargs)
    response = requests.post(url, data=data)
    return response.json()


def send_ads():
    try:
        ads_data = file_db.reading_db()['ads']
        if ads_data:
            start = ads_data['start']
            from_chat_id = ads_data['from_chat_id']
            message_id = ads_data['message_id']
            caption = ads_data['caption']
            reply_markup = ads_data['reply_markup']
            total_users = ads_data['total_users']
            end = min(start + 100, total_users)

            users = my_db.select_users_by_id(start, end)
            if users:
                logging.info(f'Send {start} {end} {len(users)}')
                for user in users:
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
                if end < total_users:
                    time.sleep(1)
                    ads_data['start'] = end
                    file_db.add_data(ads_data, key='ads')
                    send_ads()
                else:
                    file_db.add_data(False, key='ads')
                    stats_message = (
                        f"Finished sending messages.\n\n"
                        f"Total users: {total_users}\n"
                        f"Sent: {ads_data['done_count']}\n"
                        f"Failed: {ads_data['fail_count']}\n"
                        f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                        f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                    )
                    send_message_sync(from_chat_id, stats_message)
            elif users is None:
                db.reconnect()
                time.sleep(2)
            else:
                return
        else:
            pass
    except Exception as err:
        logging.error(err)



@dp.message(AdminState.send_ads, IsAdmin())
async def get_message(msg: types.Message, state: FSMContext):
    try:
        cid = msg.from_user.id
        mid = msg.message_id
        lang = msg.from_user.language_code
        data_state = await state.get_data()
        is_admin = SelectAdmin(cid=cid)

        if is_admin.send_message():
            btn = main_admin_panel_btn()
            ads_data = file_db.reading_db().get('ads')
            if ads_data:
                tx = (
                    f"Message sending is currently in progress..\n\n"
                    f"Total users: {ads_data['total_users']}\n"
                    f"Sent: {ads_data['done_count']}\n"
                    f"Failed: {ads_data['fail_count']}\n"
                    f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                    f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                )
            else:
                from_chat_id = cid
                message_id = msg.message_id
                caption = msg.caption
                reply_markup = msg.reply_markup
                count_users = db.stat()

                data = {
                    "status": True,
                    "start": 0,
                    "done_count": 0,
                    "fail_count": 0,
                    "start-time": time.time(),
                    "from_chat_id": from_chat_id,
                    "message_id": message_id,
                    "caption": caption,
                    "reply_markup": reply_markup,
                    "total_users": count_users
                }

                file_db.add_data(data, key='ads')

                tx = (
                    f"Started sending to {count_users} users.\n\n"
                    f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
                    f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                )
                time.sleep(1)
                loop = asyncio.get_event_loop()
                executor_pool = ProcessPoolExecutor()
                loop.run_in_executor(executor_pool, send_ads)

        else:
            tx = translator(
                text="❌ Unfortunately, you do not have this permission!",
                dest=lang
            )
            btn = close_btn()
            await state.clear()

        await bot.edit_message_text(chat_id=msg.from_user.id,
                                    message_id=data_state['message_id'],
                                    text=f'<b><i>{tx}</i></b>',
                                    reply_markup=btn)
        await state.update_data({"message_id": mid})

    except Exception as err:
        logging.error(err)

