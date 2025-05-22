import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from bot.filters.admin import IsAdmin, AdminFilter
from bot.keyboards.inline.admin_btn import admin_setting
from bot.keyboards.inline.close_btn import close_btn
from bot.loader import dp, bot, db, translator
from bot.states.admin_state import AdminState


@dp.message(AdminState.add_admin, IsAdmin())
async def add_admin(msg: types.Message, state: FSMContext):

    try:
        user_id = msg.from_user.id
        mid = msg.message_id 
        language_code = msg.from_user.language_code
        data = AdminFilter(user_id=user_id)
        add_admin_db = data.add_admin()
        target_user_id = int(msg.text)

        if add_admin_db:
            data_state = await state.get_data()
            btn = await admin_setting(user_id=user_id, language_code=language_code)
            text = "🔴 Failed because admin was not found!\n"

            try:
                user = await bot.get_chat(chat_id=target_user_id)
                check = db.select_admin(user_id=target_user_id) 

                if check is None:
                    db.insert_admin(user_id=target_user_id,
                                    initiator_user_id=user_id)
                    text = translator(text="✅ Admin has been successfully added\n\nName: ",
                                      dest=language_code)
                    text += f"{user.full_name}\n"
                    text += f'Username:  @{user.username}\n'
                    await bot.send_message(chat_id=target_user_id,
                                           text=f'😊Hi @{user.username}, you have been made an admin\n'
                                                f'To open the panel, use /admin ',
                                           reply_markup=close_btn())
                    btn = await admin_setting(user_id=user_id, language_code=language_code)
                else:
                    text = translator(text="✅ Admin was added before\n\nName: ",
                                      dest=language_code)
                    text += f"{user.full_name}\n"
                    text += f'Username:  @{user.username}\n'
                    text += translator(text="Add date: ",
                                       dest=language_code)
                    text += f'{check[9]}\n<code>{check[2]}</code>'
                    text += translator(text="Added by",
                                       dest=language_code)
            except Exception as err:
                logging.error(err)
                text = translator(text="🔴 Admin failed because admin was not found!\n"
                                       "The bot may not have found the admin..",
                                  dest=language_code)
            finally:
                text = translator(text=text,
                                  dest=language_code)
                await bot.edit_message_text(chat_id=user_id,
                                            message_id=data_state['message_id'],
                                            text=text,
                                            reply_markup=btn)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!',
                              dest=language_code)
            btn = close_btn()
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=mid,
                                    text=f"<b>{text}</b>",
                                    reply_markup=btn)
        await state.update_data({
            "message_id": mid
        })
    except Exception as err:
        logging.error(err)

