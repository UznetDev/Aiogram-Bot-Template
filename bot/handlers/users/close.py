from aiogram import types, F
from aiogram.fsm.context import FSMContext

from bot.loader import bot, dp, root_logger
from bot.keyboards.inline.button import MainCallback


@dp.callback_query(MainCallback.filter(F.action == "close"))
async def close(call: types.CallbackQuery, state: FSMContext):
    try:
        await state.clear()

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
    except Exception as err:
        root_logger.error(f"Error in close handler: {err}")

