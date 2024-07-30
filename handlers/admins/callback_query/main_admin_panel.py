import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.admin_btn import main_admin_panel_btn
from filters.admin import IsAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator

@dp.callback_query(AdminCallback.filter(F.action == "main_adm_panel"), IsAdmin())
async def main_panel(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code

        text = translator(text="<b><i>👩‍💻Hello, dear admin, welcome to the main panel!</i></b>", dest=lang)
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=main_admin_panel_btn(cid=cid, lang=lang))
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        logging.error(err)
