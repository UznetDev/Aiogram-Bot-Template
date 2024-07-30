import logging
from loader import dp, db
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from keyboards.inline.admin_btn import download_statistika
from aiogram import F
from aiogram.fsm.context import FSMContext
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from data.config import yil_oy_kun, soat_minut_sekund


@dp.callback_query(AdminCallback.filter(F.action == "staristika"), IsAdmin())
async def staristika(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        is_admin = SelectAdmin(cid=cid)
        if is_admin.wiew_statistika():
            stat = db.stat()
            ban = db.stat_ban()
            tx = translator(text=f"<b>👥 Bot users count:</b> <i></i>",
                            dest=lang) + str(stat) + '<b> .</b>\n' + translator(text=f"<b>⏰ Hour: </b>",
                                                                                dest=lang) + f"<i>{soat_minut_sekund}</i>\n" + translator(
                text=f"<b>📆 Date:</b>",
                dest=lang) + f'<i> {yil_oy_kun}</i>\n ' + translator(text='<b>Number of bans: </b>',
                                                                     dest=lang) + str(ban)
            btn = download_statistika(cid=cid,
                                      lang=lang)
            await state.update_data({
                "message_id": call.message.message_id
            })
        else:
            tx = translator(text=f'<b>❌ Unfortunately, you do not have this right!</b>',
                            dest=lang)
            btn = close_btn()
        await call.message.edit_text(text=tx,
                                     reply_markup=btn)
        await state.update_data({
            "message_id": mid
        })
    except Exception as err:
        logging.error(err)
