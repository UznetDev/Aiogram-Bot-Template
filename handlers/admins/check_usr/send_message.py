import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import BlockUser
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState


@dp.callback_query(IsAdmin(), BlockUser.filter(F.action == "send_message"))
async def send_message(call: types.CallbackQuery, callback_data: BlockUser, state: FSMContext):
    try:
        target_user_id = callback_data.cid
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code
        admin_check = SelectAdmin(cid=user_id)
        button = close_btn()

        if admin_check.send_message():
            text = translator(
                text="🗨 Send me the message for the user...",
                dest=language
            )
            await state.set_state(AdminState.send_message_to_user)
        else:
            text = translator(
                text="❌ Unfortunately, you do not have this permission!",
                dest=language
            )

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=message_id,
            text=f'<b><i>{text}</i></b>',
            reply_markup=button
        )

        await state.update_data({
            "message_id": call.message.message_id,
            "user_id": target_user_id
        })
    except Exception as err:
        logging.error(err)
