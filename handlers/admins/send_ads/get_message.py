import logging
import time

from aiogram import types
from aiogram.fsm.context import FSMContext

from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from keyboards.inline.admin_btn import main_admin_panel_btn
from keyboards.inline.close_btn import close_btn
from loader import dp, db, bot
from states.admin_state import AdminState


@dp.message(AdminState.send_ads, IsAdmin())
async def send_ads_message(msg: types.Message, state: FSMContext):
    try:
        cid = msg.from_user.id
        mid = msg.message_id
        lang = msg.from_user.language_code
        data_state = await state.get_data()
        is_admin = SelectAdmin(cid=cid)
        btn = close_btn()
        if is_admin.send_message():
            users = db.stat()
            text = translator(text=f"📢 Advertising sending started...\n"
                                   f'📊 Number of users: {users}\n'
                                   f"🕒 Wait...\n",
                              dest=lang)
            await bot.edit_message_text(chat_id=msg.from_user.id,
                                        message_id=data_state['message_id'],
                                        text=f'<b><i>{text}</i></b>',
                                        reply_markup=close_btn())
            try:
                user = db.select_all_users()
                count_done = 0
                count_not_done = 0
                for i in user:
                    try:
                        await bot.copy_message(chat_id=i[1],
                                               from_chat_id=msg.chat.id,
                                               message_id=msg.message_id,
                                               caption=msg.caption,
                                               reply_markup=msg.reply_markup)
                        time.sleep(0.1)
                        count_done += 1
                    except Exception as err:
                        count_not_done += 1
                        logging.error(err)
                btn = main_admin_panel_btn(cid=cid,
                                           lang=lang)
                tx = translator(text=f"🔰 Ad successfully sent!\n"
                                     f' ✅ Sent successfully! {count_done}\n'
                                     f"🔴 Sending failed! {count_not_done}\n\n",
                                dest=lang)
                await state.clear()
                await state.update_data({
                    "message_id": msg.message_id
                })
            except Exception as err:
                tx = translator(text=f'Something wrong ERROR: ',
                                dest=lang) + err
                await state.clear()
                logging.error(err)
        else:
            tx = translator(text=f'❌ Unfortunately, you do not have this right!',
                            dest=lang)
            btn = close_btn()
            await state.clear()
        await bot.edit_message_text(chat_id=msg.from_user.id,
                                    message_id=data_state['message_id'],
                                    text=f'<b><i>{tx}</i></b>',
                                    reply_markup=btn)
        await state.update_data({
            "message_id": mid
        })
    except Exception as err:
        logging.error(err)
