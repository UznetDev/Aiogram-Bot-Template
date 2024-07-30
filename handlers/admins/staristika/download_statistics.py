import logging
import pandas
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
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        is_admin = SelectAdmin(cid=cid)
        if is_admin.download_statistika():
            data = db.select_all_users()
            id_list = []
            cid_list = []
            date_list = []
            username = []
            langs = []
            for x in data:
                id_list.append(x[0])
                cid_list.append(x[1])
                date_list.append(x[2])
                langs.append(x[3])
                usernames = await bot.get_chat(chat_id=x[1])
                username.append(f'@{usernames.username}')
            x_data = {"id": id_list,
                      "cid": cid_list,
                      "date_add": date_list,
                      "username": username,
                      "lang": langs}
            new_data = pandas.DataFrame(x_data)
            new_data.to_excel('statistics.xlsx', index=False)
            document = types.input_file.FSInputFile(path='statistics.xlsx')
            stat = db.stat()
            tx = translator(text=f"✅Downloaded! \n\n</b>",
                            dest=lang) + translator(text=f"<b>👥 Bot users count:</b> <i></i>",
                                                    dest=lang) + str(stat) + '<b> nafar.</b>\n' + translator(text=f"<b>⏰ Hour: </b>",
                                                                                                             dest=lang) + f"<i>{soat_minut_sekund}</i>\n" + translator(text=f"<b>📆 Date:</b>",
                                                                                                                                                                       dest=lang) + f'<i> {yil_oy_kun}</i>'
            await bot.send_document(chat_id=cid,
                                    document=document,
                                    caption=tx)
            tx = translator(text=f"<b>✅Downloaded!</b>\n",
                            dest=lang)
            await state.update_data({
                "message_id": call.message.message_id
            })
        else:
            tx = translator(text=f'<b>❌ Unfortunately, you do not have this right!</b>',
                            dest=lang)
        await call.message.edit_text(text=tx,
                                     reply_markup=close_btn())
        await state.update_data({
            "message_id": mid
        })
    except Exception as err:
        logging.error(err)
