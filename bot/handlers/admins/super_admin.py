import os
import pandas as pd
from aiogram import types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from bot.data.config import log_file_name
from bot.filters.admin import IsSuperAdmin
from bot.loader import dp, bot, db, root_logger


@dp.message(IsSuperAdmin(), Command(commands='stat'))
async def super_admin(msg: types.Message):
    try:
        root_logger.info('Generating stats report')
        user_id = msg.from_user.id
        mid = msg.message_id
        data = db.select_all_users_ban()

        id_list = []
        user_id_list = []
        date_list = []
        username_list = []
        admin_user_id = []

        try:
            if data:
                for x in data:
                    id_list.append(x['id'])
                    user_id_list.append(x['user_id'])
                    admin_user_id.append(x['initiator_user_id'])
                    date_list.append(x['ban_time'])

                    # Fetching username from chat ID
                    chat = await bot.get_chat(chat_id=x['user_id'])
                    username_list.append(f'@{chat.username}')

                x_data = {
                    "id": id_list,
                    "user_id": user_id_list,
                    "admin_user_id": admin_user_id,
                    "date_add": date_list,
                    "username": username_list
                }
                df = pd.DataFrame(x_data)
                excel_path = 'data/ban.xlsx'
                df.to_excel(excel_path, index=False)

                document = FSInputFile(excel_path)
                await bot.send_document(
                    chat_id=user_id,
                    document=document,
                    caption='<b>Ban list</b>'
                )
                os.remove(excel_path)

        except Exception as err:
            root_logger.error(f"Error processing ban data: {err}")

        try:
            if os.path.exists(log_file_name) and os.path.getsize(log_file_name) > 0:
                document2 = FSInputFile(log_file_name)
                await bot.send_document(
                    chat_id=user_id,
                    document=document2,
                    caption='<b>Update log</b>'
                )
        except Exception as err:
            root_logger.error(f"Error sending log file: {err}")

        await bot.delete_message(chat_id=user_id, message_id=mid)

    except Exception as err:
        root_logger.error(f"Unhandled error: {err}")