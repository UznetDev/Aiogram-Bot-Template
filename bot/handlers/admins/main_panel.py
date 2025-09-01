from bot.loader import dp, bot, translator, root_logger
from bot.keyboards.inline.admin_btn import main_admin_panel_btn
from bot.filters.admin import IsAdmin

from aiogram.filters import Command
from aiogram import types

from aiogram.fsm.context import FSMContext


@dp.message(Command(commands='admin'), IsAdmin())
async def main_panel(msg: types.Message, state: FSMContext):
    try:
        user_id = msg.from_user.id
        message_id = msg.message_id
        language_code = msg.from_user.language_code

        welcome_text = translator(text=f'👩‍💻Hello, dear admin, welcome to the main panel!',
                                  dest=language_code)
        response_msg = await msg.answer(text=f'<b>{welcome_text}</b>',
                                        reply_markup=main_admin_panel_btn(user_id=user_id, language_code=language_code))

        state_data = await state.get_data()
        try:
            if 'message_id' in state_data and state_data['message_id'] > 1:
                await bot.delete_message(chat_id=user_id, message_id=state_data['message_id'])
        except Exception as err:
            root_logger.error(f"Error deleting previous message: {err}")

        await state.update_data({
            "message_id": response_msg.message_id
        })

        await bot.delete_message(chat_id=user_id, message_id=message_id)

    except Exception as err:
        root_logger.error(f"Unhandled error: {err}")

