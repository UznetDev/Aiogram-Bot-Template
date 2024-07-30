import logging
from loader import dp, bot
from aiogram import types
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState


@dp.message(AdminState.send_message_to_user, IsAdmin())
async def send_ads_message(msg: types.Message, state: FSMContext):
    try:
        user_id = msg.from_user.id
        language = msg.from_user.language_code
        data_state = await state.get_data()
        target_user_id = data_state['user_id']
        is_admin = SelectAdmin(cid=user_id)
        button = close_btn()

        if is_admin.send_message():
            try:
                await bot.copy_message(
                    chat_id=target_user_id,
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    reply_markup=msg.reply_markup
                )
                text = translator(
                    text='<b>✅ Message sent</b>',
                    dest=language
                )
            except Exception as err:
                text = translator(
                    text='<b>Something went wrong. ERROR:</b>',
                    dest=language
                ) + str(err)
                await state.clear()
                logging.error(err)
        else:
            text = translator(
                text='<b>❌ Unfortunately, you do not have this permission!</b>',
                dest=language
            )
            await state.clear()

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=data_state['message_id'],
            text=text,
            reply_markup=button
        )
        await state.clear()
        await state.update_data({"message_id": msg.message_id})

    except Exception as err:
        logging.error(err)
