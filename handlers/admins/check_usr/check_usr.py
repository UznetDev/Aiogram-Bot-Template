import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState


@dp.callback_query(AdminCallback.filter(F.action == "check_user"), IsAdmin())
async def check_user(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code
        data = SelectAdmin(cid=user_id)
        button = close_btn()

        if data.block_user():
            text = translator(
                text='<b><i>🔰Please send the user ID you want to check...</i></b>',
                dest=language
            )
            await state.set_state(AdminState.check_user)
        else:
            text = translator(
                text='<b>❌ Unfortunately, you do not have the required permissions!</b>',
                dest=language
            )

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=message_id,
            text=text,
            reply_markup=button
        )

        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        logging.error(err)