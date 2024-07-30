import logging
import pandas
import os
from aiogram import types
from aiogram.filters import Command
from data.config import log_file_name
from filters.admin import IsSuperAdmin
from loader import dp, bot, db


@dp.message(IsSuperAdmin(), Command(commands='stat'))
async def super_admin(msg: types.Message):
    try:
        logging.info('include log')
        cid = msg.from_user.id
        mid = msg.message_id
        data = db.select_all_users_ban()
        id_list = []
        cid_list = []
        date_list = []
        username = []
        admin_cid = []
        try:
            for x in data:
                id_list.append(x[0])
                cid_list.append(x[1])
                admin_cid.append(x[2])
                date_list.append(x[3])
                usernames = await bot.get_chat(chat_id=x[1])
                username.append(f'@{usernames.username}')
            x_data = {"id": id_list,
                      "cid": cid_list,
                      "add_cid": admin_cid,
                      "date_add": date_list,
                      "username": username}
            new_data = pandas.DataFrame(x_data)
            new_data.to_excel('data/ban.xlsx', index=False)
            document = types.input_file.FSInputFile(path='data/ban.xlsx')
            await bot.send_document(chat_id=cid,
                                    document=document,
                                    caption=f'<b>Ban list</b>')
            os.remove('db/ban.xlsx')
        except Exception as err:
            logging.error(err)
        try:
            if os.path.exists(log_file_name) and os.path.getsize(log_file_name):
                document2 = types.input_file.FSInputFile(path=log_file_name)
                await bot.send_document(chat_id=cid,
                                        document=document2,
                                        caption=f'<b>Update log</b>')
        except Exception as err:
            logging.error(err)
        await bot.delete_message(chat_id=cid, message_id=mid)
    except Exception as err:
        logging.error(err)
