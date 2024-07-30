import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from filters.admin import IsAdmin, SelectAdmin
from function.translator import translator
from keyboards.inline.admin_btn import admin_setting
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from loader import dp, bot

@dp.callback_query(AdminCallback.filter(F.action == "admin_settings"), IsAdmin())
async def admin_settings(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        add_admin = data.add_admin()
        if add_admin:
            text = translator(text="❗ You are in the Admin settings section!", dest=lang)
            btn = await admin_setting(cid=cid, lang=lang)
        else:
            text = translator(text="❌ Unfortunately, you do not have this right!", dest=lang)
            btn = close_btn()
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=f'<b>{text}</b>', reply_markup=btn)
        await state.update_data({"message_id": mid})
    except Exception as err:
        logging.error(err)
