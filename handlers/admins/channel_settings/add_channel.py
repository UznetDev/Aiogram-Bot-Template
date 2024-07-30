import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState


@dp.callback_query(AdminCallback.filter(F.action == "add_channel"), IsAdmin())
async def add_channel(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        btn = close_btn()
        if data.channel_settings():
            await state.set_state(AdminState.add_channel)
            text = translator(text="😊 Please send the channel id...", dest=lang)
            await state.update_data({"message_id": call.message.message_id})
        else:
            text = translator(text="❌ Unfortunately, you do not have this right!", dest=lang)
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=f'{text}', reply_markup=btn)
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        logging.error(err)