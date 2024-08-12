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
        Initialize the MyDatabase object with connection parameters.

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
        Select users from the 'users' table by their ID.

        :param start_id: The starting ID (inclusive).
        :param end_id: The ending ID (exclusive).

        :return list: A list of tuples containing user data.
        """
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


my_db = MyDatabase(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)


def copy_message_sync(chat_id, from_chat_id, message_id, **kwargs):
    """
    Synchronously copy a message from one chat to another using the Telegram API.

    :param chat_id: The target chat ID where the message will be copied.
    :param from_chat_id: The chat ID where the message originates.
    :param message_id: The ID of the message to copy.
    :param kwargs: Additional optional parameters for the API request.

    :return dict: The JSON response from the Telegram API.
    """
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
    """
    Synchronously send a message to a specific chat using the Telegram API.

    :param chat_id: The target chat ID where the message will be sent.
    :param text: The text of the message to send.
    :param kwargs: Additional optional parameters for the API request.

    :return dict: The JSON response from the Telegram API.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    data.update(kwargs)
    response = requests.post(url, data=data)
    return response.json()


def send_ads():
    """
    Function to handle the advertisement sending process.

    This function reads the advertisement data from the database, selects a batch of users,
    and sends the advertisement message to each user. It updates the advertisement progress
    and logs any errors that occur. If the entire batch of users is processed, it terminates
    the sending process and updates the status in the database.
    """
    try:
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
                    ads_data['start'] = end_index
                    file_db.add_data(ads_data, key='ads')
                    send_ads()  # Recursive call to continue sending to the next batch
                else:
                    file_db.add_data(False, key='ads')
                    summary_message = (
                        f"📬 <b>Advertisement Sending Completed</b>\n\n"
                        f"👥 <b>Total Users:</b> {total_users}\n"
                        f"✅ <b>Sent:</b> {ads_data['done_count']}\n"
                        f"❌ <b>Failed:</b> {ads_data['fail_count']}\n"
                        f"⏰ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                        f"🕒 <b>End Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                    )
                    send_message_sync(from_chat_id, summary_message)
            elif users_batch is None:
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
    """
    Handles the "send_ads" state in the admin panel, checking if the user is an admin and
    updating the advertisement sending process.

    This function retrieves the current state of the advertisement campaign, provides feedback
    to the admin on its progress, and initiates the sending process if necessary.

    Args:
        msg (types.Message): The incoming message from the admin.
        state (FSMContext): The FSM context for managing the conversation state.

    Returns:
        None: Sends a message to the admin with the advertisement process status.

    Raises:
        Exception: Logs any exceptions that occur during execution.
    """
    try:
        # Extract user and message details
        user_id = msg.from_user.id
        message_id = msg.message_id
        language_code = msg.from_user.language_code
        state_data = await state.get_data()

        # Check if the user has admin permissions
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.send_message():
            # Prepare the admin panel button and fetch ads data
            button_markup = main_admin_panel_btn(cid=user_id, lang=language_code)
            ads_data = file_db.reading_db().get('ads')

            if ads_data:
                # If ads are in progress, provide status update
                message_text = (
                    f"📢 <b>Advertisement Status:</b>\n\n"
                    f"👥 <b>Total Users:</b> {ads_data['total_users']}\n"
                    f"✅ <b>Messages Sent:</b> {ads_data['done_count']}\n"
                    f"❌ <b>Failed Messages:</b> {ads_data['fail_count']}\n"
                    f"⏳ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                    f"🕒 <b>Current Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                )
            else:
                # If no ads are in progress, start a new ad campaign
                from_chat_id = user_id
                caption = msg.caption
                reply_markup = msg.reply_markup
                total_users = db.stat()

                new_ads_data = {
                    "status": True,
                    "start": 0,
                    "done_count": 0,
                    "fail_count": 0,
                    "start-time": time.time(),
                    "from_chat_id": from_chat_id,
                    "message_id": message_id,
                    "caption": caption,
                    "reply_markup": reply_markup,
                    "total_users": total_users
                }

                file_db.add_data(new_ads_data, key='ads')

                message_text = (
                    f"🚀 <b>Started sending to {total_users} users.</b>\n\n"
                    f"⏰ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
                    f"🕒 <b>End Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                )

                # Start the ad sending process in a separate thread
                time.sleep(1)
                loop = asyncio.get_event_loop()
                executor_pool = ProcessPoolExecutor()
                loop.run_in_executor(executor_pool, send_ads)

        else:
            # If the user is not an admin, send a permission error message
            message_text = translator(
                text="❌ Unfortunately, you do not have this permission!",
                dest=language_code
            )
            button_markup = close_btn()
            await state.clear()

        # Update the message with the new content and buttons
        await bot.edit_message_text(
            chat_id=msg.from_user.id,
            message_id=state_data['message_id'],
            text=f'<b><i>{message_text}</i></b>',
            reply_markup=button_markup
        )

        # Update the state with the current message ID
        await state.update_data({"message_id": message_id})

    except Exception as err:
        logging.error(f"Error in get_message: {err}")

