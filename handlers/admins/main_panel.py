import logging
from loader import dp, bot
from aiogram.filters import Command
from aiogram import types
from keyboards.inline.admin_btn import main_admin_panel_btn
from filters.admin import IsAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator


@dp.message(Command(commands='admin'), IsAdmin())
async def main_panel(msg: types.Message, state: FSMContext):
    try:
        cid = msg.from_user.id
        mid = msg.message_id
        lang = msg.from_user.language_code
        tx = translator(text=f'<b><i>👩‍💻Hello, dear admin, welcome to the main panel!</i></b>',
                        dest=lang)
        msg = await msg.answer(text=tx,
                               reply_markup=main_admin_panel_btn(cid=cid,
                                                                 lang=lang))
        data = await state.get_data()
        try:
            if data['message_id'] > 1:
                await bot.delete_message(chat_id=cid, message_id=data['message_id'])
        except Exception as err:
            pass
        await state.update_data({
            "message_id": msg.message_id
        })
        await bot.delete_message(chat_id=cid, message_id=mid)
    except Exception as err:
        logging.error(err)
