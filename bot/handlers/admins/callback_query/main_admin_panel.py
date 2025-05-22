from aiogram import types, F
from aiogram.fsm.context import FSMContext

from bot.loader import dp, bot, translator, root_logger
from bot.keyboards.inline.button import AdminCallback
from bot.keyboards.inline.admin_btn import main_admin_panel_btn
from bot.filters.admin import IsAdmin


@dp.callback_query(AdminCallback.filter(F.action == "main_adm_panel"), IsAdmin())
async def main_panel(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id
        mid = call.message.message_id
        language_code = call.from_user.language_code 

        text = translator(text="👩‍💻Hello, dear admin, welcome to the main panel!", 
                          dest=language_code)

        await bot.edit_message_text(chat_id=user_id,
                                    message_id=mid,
                                    text=f'{text}',
                                    reply_markup=main_admin_panel_btn(user_id=user_id, language_code=language_code))

        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        root_logger.error(err)

