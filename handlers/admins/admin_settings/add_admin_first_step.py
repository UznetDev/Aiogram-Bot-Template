import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from filters.admin import IsAdmin, SelectAdmin
from function.translator import translator
from keyboards.inline.admin_btn import admin_setting
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from loader import dp, bot
from states.admin_state import AdminState


@dp.callback_query(AdminCallback.filter(F.action == "add_admin"), IsAdmin())
async def add_admin_first(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        add_admin = data.add_admin()
        if add_admin:
            text = translator(text="<b><i>🔰 Please send the admin ID number you want to add...</i></b>", dest=lang)
            btn = await admin_setting(cid=cid, lang=lang)
            await state.set_state(AdminState.add_admin)
        else:
            text = translator(text="<b>❌ Unfortunately, you do not have this right!</b>", dest=lang)
            btn = close_btn()
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=btn)
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        logging.error(err)
