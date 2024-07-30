import logging
from loader import bot, dp
from aiogram.fsm.context import FSMContext
from keyboards.inline.button import MainCallback
from aiogram import types, F


@dp.callback_query(MainCallback.filter(F.action == "close"))
async def close(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the close callback action.
    Clears the FSM context and deletes the message that triggered the callback query.

    Args:
        call (types.CallbackQuery): The callback query.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    try:
        # Clear the FSM context
        await state.clear()

        # Delete the message that triggered the callback query
        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
    except Exception as err:
        logging.error(f"Error in close handler: {err}")

