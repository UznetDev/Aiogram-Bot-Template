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


@dp.callback_query(AdminCallback.filter(F.action == "statistika"), IsAdmin())
async def statistika(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.wiew_statistika():
            user_count = db.stat()
            ban_count = db.stat_ban()
            text = (translator(text="<b>👥 Bot users count:</b> <i>", dest=language) + str(user_count) +
                    '</i><b> .</b>\n' + translator(text="<b>⏰ Time:</b>", dest=language) +
                    f" <i>{soat_minut_sekund}</i>\n" + translator(text="<b>📆 Date:</b>", dest=language) +
                    f' <i>{yil_oy_kun}</i>\n ' + translator(text="<b>Number of bans:</b> ", dest=language) + str(
                        ban_count))
            button = download_statistika(cid=user_id, lang=language)
            await state.update_data({"message_id": call.message.message_id})
        else:
            text = translator(text="<b>❌ Unfortunately, you do not have this permission!</b>", dest=language)
            button = close_btn()

        await call.message.edit_text(text=text, reply_markup=button)
        await state.update_data({"message_id": message_id})

    except Exception as err:
        logging.error(err)
