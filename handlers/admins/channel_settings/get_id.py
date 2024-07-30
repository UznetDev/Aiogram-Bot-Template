import logging
from loader import dp, bot, db
from aiogram import types
from keyboards.inline.admin_btn import channel_settings
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState
from data.config import yil_oy_kun, soat_minut_sekund


@dp.message(AdminState.add_channel, IsAdmin())
async def add_channel2(msg: types.Message, state: FSMContext):
    try:
        cid = msg.from_user.id
        mid = msg.message_id
        lang = msg.from_user.language_code
        data = SelectAdmin(cid=cid)
        btn = close_btn()
        data_state = await state.get_data()

        if data.channel_settings():
            try:
                tx = msg.text
                k_id = int(str(-100) + str(tx))
                channel = await bot.get_chat(chat_id=k_id)
                check = db.check_channel(cid=tx)

                if check is None:
                    db.add_channel(cid=tx,
                                   date=str(yil_oy_kun) + ' / ' + str(soat_minut_sekund),
                                   add_cid=cid)
                    text = translator(text="<b>✅ The channel was successfully added</b>\n",
                                      dest=lang) + f"<b>Name:</b> <i>{channel.full_name}</i>\n" \
                                                   f"<b>Username:</b> <i>@{channel.username}</i>"
                else:
                    text = translator(text="<b>✅ The channel was previously added</b>\n",
                                      dest=lang) + f"<b>Name:</b> <i>{channel.full_name}</i>\n" \
                                                   f"<b>Username:</b> <i>@{channel.username}</i>\n" \
                                                   f"<b>Added date:</b> <i>{check[3]}</i>"

                btn = channel_settings(lang=lang)
            except Exception as err:
                text = translator(text="<b>🔴 The channel could not be added because the channel was not found!</b>\n"
                                       "<i>The bot is not an admin on the channel.</i>",
                                  dest=lang)
                logging.error(err)
            await state.clear()
        else:
            text = translator(text='<b>❌ Unfortunately, you do not have this right!</b>',
                              dest=lang)

        await bot.edit_message_text(chat_id=cid,
                                    message_id=data_state['message_id'],
                                    text=text,
                                    reply_markup=btn)
        await state.update_data({
            "message_id": mid
        })
    except Exception as err:
        logging.error(err)
