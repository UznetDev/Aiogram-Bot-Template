import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from filters.admin import IsAdmin, SelectAdmin
from function.translator import translator
from keyboards.inline.admin_btn import admin_setting
from keyboards.inline.close_btn import close_btn
from loader import dp, bot, db
from states.admin_state import AdminState
from data.config import yil_oy_kun, soat_minut_sekund


@dp.message(AdminState.add_admin, IsAdmin())
async def add_admin(msg: types.Message, state: FSMContext):
    try:
        cid = msg.from_user.id
        mid = msg.message_id
        lang = msg.from_user.language_code
        data = SelectAdmin(cid=cid)
        add_admin_db = data.add_admin()
        user_id = int(msg.text)
        if add_admin_db:
            data_state = await state.get_data()
            btn = await admin_setting(cid=cid, lang=lang)
            text = "🔴 Admin failed because admin was not found!\n"
            try:
                user = await bot.get_chat(chat_id=user_id)
                check = db.select_admin(cid=user_id)
                if check is None:
                    logging.info(user_id)
                    logging.info(cid)
                    db.add_admin(cid=user_id,
                                 date=f"{yil_oy_kun} / {soat_minut_sekund}",
                                 add=cid)
                    text = translator(text="✅ Admin has been successfully added\n\nName: ",
                                      dest=lang)
                    text += f"{user.full_name}\n"
                    text += f'Username:  @{user.username}\n'
                    await bot.send_message(chat_id=user_id,
                                           text=f'😊Hi @{user.username}, you have been made an admin\n'
                                                f'To open the panel, use /admin ',
                                           reply_markup=close_btn())
                else:
                    logging.info(type(check[1]))
                    logging.info(check[9])
                    text = translator(text="✅ Admin was added before\n\nName: ",
                                      dest=lang)
                    text += f"{user.full_name}\n"
                    text += f'Username:  @{user.username}\n'
                    text += translator(text="Add date: ",
                                       dest=lang)
                    text += f'{check[9]}\n<code>{check[2]}</code>'
                    text += translator(text="Added by",
                                       dest=lang)
            except Exception as err:
                logging.error(err)
                text = translator(text="🔴 Admin failed because admin was not found!\n"
                                       "The bot may not have found the admin..",
                                  dest=lang)
            finally:
                text = translator(text=text,
                                  dest=lang)
                await bot.edit_message_text(chat_id=cid,
                                            message_id=data_state['message_id'],
                                            text=text,
                                            reply_markup=btn)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!',
                              dest=lang)
            btn = close_btn()
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f"<b>{text}</b>",
                                    reply_markup=btn)
        await state.update_data({
            "message_id": mid
        })
    except Exception as err:
        logging.error(err)
