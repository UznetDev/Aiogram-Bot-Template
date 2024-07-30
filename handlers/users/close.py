import logging
from loader import bot, dp
from aiogram.fsm.context import FSMContext
from keyboards.inline.button import MainCallback
from aiogram import types, F


@dp.callback_query(MainCallback.filter(F.action == "close"))
async def close(call: types.CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)
    except Exception as err:
        logging.error(err)
