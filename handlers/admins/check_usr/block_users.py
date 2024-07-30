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
async def block_users(call: types.CallbackQuery, callback_data: BlockUser, state: FSMContext):
    try:
        user_id = callback_data.cid
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
                    text = translator(text='⛔ User blocked\n\n Username: @',
                                       dest=lang)
                    text += str(user.username)
                    await bot.send_message(chat_id=user_id,
                                           text='🚫 You are blocked!'
                                                '⚠ If you think this is a mistake, contact the admin.',
                                           reply_markup=close_btn())
                else:
                    if check[2] == cid or cid == ADMIN:
                        db.delete_user_ban(cid=user_id)
                        text = translator(text='✅ User unblocked!\n\n Username: @', dest=lang)
                        text += str(user.username)
                        await bot.send_message(chat_id=user_id,
                                               text='😊 You are unblocked!'
                                                    'Contact the admin',
                                               reply_markup=close_btn())
                    else:
                        text = translator(text='⭕ Only the person who blocked the user can unblock them!\n\n '
                                               'Username: @',
                                          dest=lang)
                        text += str(user.username)
            else:
                text = translator(text='🚫 I cannot block an admin.',
                                  dest=lang)
                try:
                    db.delete_user_ban(cid=user_id)
                except Exception as err:
                    logging.error(err)
            await state.set_state(AdminState.check_user)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=lang)
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        logging.error(err)