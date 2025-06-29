import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from bot.filters.admin import IsAdmin
from bot.keyboards.inline.admin_btn import admin_setting
from bot.keyboards.inline.button import AdminCallback
from bot.keyboards.inline.close_btn import close_btn
from bot.loader import dp, bot, translator, AM



@dp.callback_query(AdminCallback.filter(F.action == "admin_settings"), IsAdmin())
async def admin_settings(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id
        mid = call.message.message_id
        language_code = call.from_user.language_code

        if AM[user_id]:
            text = translator(text="❗ You are in the Admin settings section!", dest=language_code)
            btn = await admin_setting(user_id=user_id, language_code=language_code)
        else:
            text = translator(text="❌ Unfortunately, you do not have this right!", dest=language_code)
            btn = close_btn()

        await bot.edit_message_text(chat_id=user_id,
                                    message_id=mid,
                                    text=f'<b>{text}</b>',
                                    reply_markup=btn)
        await state.update_data({"message_id": mid})
    except Exception as err:
        logging.error(err)

