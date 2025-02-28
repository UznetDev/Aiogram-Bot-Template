import logging
import pandas as pd
import os
from aiogram import types
from aiogram.filters import Command
from data.config import log_file_name
from filters.admin import IsSuperAdmin
from loader import dp, bot, db
from aiogram.types import FSInputFile


@dp.message(IsSuperAdmin(), Command(commands='stat'))
async def super_admin(msg: types.Message):
    """
    Handles the '/stat' command from super admins to generate and send a report
    of banned users and system logs.

    This function performs the following steps:
    1. Logs the initiation of the stats report generation process.
    2. Retrieves the user ID and message ID from the incoming message.
    3. Fetches all banned users' data from the database.
    4. Constructs a DataFrame with the banned users' details including their IDs,
       chat IDs, admin chat IDs, dates of ban, and usernames.
    5. Saves the DataFrame to an Excel file and sends it to the super admin.
    6. Deletes the Excel file from the filesystem after sending.
    7. Checks if the log file exists and is not empty, then sends it to the super admin.
    8. Deletes the original message from the chat.

    Args:
        msg (types.Message): The incoming message object containing details of the command.

    Raises:
        Exception: Logs any exceptions that occur during the process.

    Returns:
        None
    """
    try:
        logging.info('Generating stats report')
        user_ud = msg.from_user.id
        mid = msg.message_id
        data = db.select_all_users_ban()

        id_list = []
        user_ud_list = []
        date_list = []
        username_list = []
        admin_user_ud = []

        try:
            # Collecting data for the DataFrame
            for x in data:
                id_list.append(x['id'])
                user_ud_list.append(x['user_id'])
                admin_user_ud.append(x['admin_user_id'])
                date_list.append(x['date'])

                # Fetching username from chat ID
                chat = await bot.get_chat(chat_id=x['user_id'])
                username_list.append(f'@{chat.username}')

            # Creating and saving DataFrame to Excel
            x_data = {
                "id": id_list,
                "user_ud": user_ud_list,
                "admin_user_ud": admin_user_ud,
                "date_add": date_list,
                "username": username_list
            }
            df = pd.DataFrame(x_data)
            excel_path = 'data/ban.xlsx'
            df.to_excel(excel_path, index=False)

            # Sending the generated Excel file using FSInputFile
            document = FSInputFile(excel_path)
            await bot.send_document(
                chat_id=user_ud,
                document=document,
                caption='<b>Ban list</b>'
            )
            os.remove(excel_path)

        except Exception as err:
            logging.error(f"Error processing ban data: {err}")

        try:
            # Sending the log file if it exists
            if os.path.exists(log_file_name) and os.path.getsize(log_file_name) > 0:
                document2 = FSInputFile(log_file_name)
                await bot.send_document(
                    chat_id=user_ud,
                    document=document2,
                    caption='<b>Update log</b>'
                )
        except Exception as err:
            logging.error(f"Error sending log file: {err}")

        # Deleting the original message
        await bot.delete_message(chat_id=user_ud, message_id=mid)

    except Exception as err:
        logging.error(f"Unhandled error: {err}")