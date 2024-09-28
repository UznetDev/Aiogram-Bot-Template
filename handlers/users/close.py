import logging
import time
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
    start_time = time.perf_counter()
    user_id = call.message.chat.id
    user_language = call.message.from_user.language_code
    try:
        # Clear the FSM context
        await state.clear()

        # Delete the message that triggered the callback query
        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.info(f"Close",
                     extra={
                         'chat_id': user_id,
                         'language_code': user_language,
                         'execution_time': execution_time
                     })
    except Exception as err:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.info(f"Error in close handler: {err}",
                     extra={
                         'chat_id': user_id,
                         'language_code': user_language,
                         'execution_time': execution_time
                     })

