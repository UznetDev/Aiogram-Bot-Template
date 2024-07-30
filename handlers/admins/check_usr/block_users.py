import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import BlockUser
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState
from data.config import yil_oy_kun, soat_minut_sekund, ADMIN


@dp.callback_query(BlockUser.filter(F.action == "block"), IsAdmin())
async def block_users(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.data.split(':')[2]
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        btn = close_btn()
        if data.block_user():
            check1 = db.select_admin(cid=user_id)
            if check1 is None:
                check = db.check_user_ban(cid=user_id)
                user = await bot.get_chat(chat_id=user_id)
                if check is None:
                    db.add_user_ban(cid=user_id,
                                    admin_cid=cid,
                                    date=f'{yil_oy_kun} / {soat_minut_sekund}')
                    text = (translator(text='<b><i>⛔ User blocked\n\n Username: @</i></b>', dest=lang) +
                            str(user.username))
                    await bot.send_message(chat_id=user_id,
                                           text='<b>🚫 You are blocked!</b>'
                                                '<i>⚠ If you think this is a mistake, contact the admin.</i>',
                                           reply_markup=close_btn())
                else:
                    if check[2] == cid or cid == ADMIN:
                        db.delete_user_ban(cid=user_id)
                        text = (translator(text='<b><i>✅ User unblocked!\n\n Username: @</i></b>', dest=lang) +
                                str(user.username))
                        await bot.send_message(chat_id=user_id,
                                               text='<b>😊 You are unblocked!</b>'
                                                    '<i>Contact the admin</i>',
                                               reply_markup=close_btn())
                    else:
                        text = (translator(text='<b><i>⭕ Only the person who blocked the user can unblock them!\n\n '
                                                'Username: @</i></b>', dest=lang) +
                                str(user.username))
            else:
                text = translator(text='<b><i>🚫 I cannot block an admin.</i></b>', dest=lang)
                try:
                    db.delete_user_ban(cid=user_id)
                except Exception as err:
                    logging.error(err)
            await state.set_state(AdminState.check_user)
        else:
            text = translator(text='<b>❌ Unfortunately, you do not have this right!</b>', dest=lang)
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=text,
                                    reply_markup=btn)
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        logging.error(err)