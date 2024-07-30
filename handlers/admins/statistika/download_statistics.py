import logging
import os
import pandas as pd
from loader import dp, db, bot
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from aiogram import F
from aiogram.fsm.context import FSMContext
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from data.config import yil_oy_kun, soat_minut_sekund


@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "download_statistika"))
async def download_statistics(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.download_statistika():
            data = db.select_all_users()
            id_list = []
            cid_list = []
            date_list = []
            usernames = []
            langs = []

            for user in data:
                id_list.append(user[0])
                cid_list.append(user[1])
                date_list.append(user[2])
                langs.append(user[3])
                user_info = await bot.get_chat(chat_id=user[1])
                usernames.append(f'@{user_info.username}')

            statistics_data = {
                "id": id_list,
                "cid": cid_list,
                "date_add": date_list,
                "username": usernames,
                "lang": langs
            }
            df = pd.DataFrame(statistics_data)
            df.to_excel('db/statistics.xlsx', index=False)

            document = types.input_file.FSInputFile(path='db/statistics.xlsx')
            user_count = db.stat()

            text = (translator(text="<b>✅ Downloaded! \n\n</b>", dest=language) +
                    translator(text="<b>👥 Bot users count:</b> <i>", dest=language) +
                    str(user_count) + '<b> .</b>\n' +
                    translator(text="<b>⏰ Time:</b>", dest=language) +
                    f"<i>{soat_minut_sekund}</i>\n" +
                    translator(text="<b>📆 Date:</b>", dest=language) +
                    f"<i> {yil_oy_kun}</i>")

            await bot.send_document(chat_id=user_id, document=document, caption=text)
            os.remove('db/statistics.xlsx')

            text = translator(text="<b>✅ Downloaded!</b>\n", dest=language)
            await state.update_data({"message_id": call.message.message_id})
        else:
            text = translator(text="<b>❌ Unfortunately, you do not have this permission!</b>", dest=language)

        await call.message.edit_text(text=text, reply_markup=close_btn())
        await state.update_data({"message_id": message_id})

    except Exception as err:
        logging.error(err)
