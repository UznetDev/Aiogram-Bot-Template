import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from data.config import ADMIN


@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "delete_channel"))
async def delete_channel(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        btn = close_btn()

        if data.channel_settings():
            ch_cid = call.data.split(':')[2]
            ch_cid100 = str(-100) + str(ch_cid)
            check = db.check_channel(cid=ch_cid)

            if not check:
                text = translator(
                    text='<b>⭕ Channel not found!</b>\n<i>The channel seems to have been deleted previously!</i>',
                    dest=lang)
            else:
                channel = await bot.get_chat(chat_id=ch_cid100)

                if check[3] == cid or cid == ADMIN:
                    db.delete_channel(cid=ch_cid)
                    tx = translator(text='<b><i>🚫 Channel removed...</i></b>\n',
                                    dest=lang)
                    text = (f"{tx}\n"
                            f"<b>Name:</b> <i>{channel.full_name}</i>\n"
                            f"<b>Username:</b> <i>@{channel.username}</i>\n"
                            f"<b>ID:</b> <i><code>{ch_cid}</code></i>\n\n")
                else:
                    text = translator(text='<b>⭕ Only an admin can delete this channel</b>',
                                      dest=lang)
        else:
            text = translator(text='<b>❌ Unfortunately, you do not have this right!</b>',
                              dest=lang)

        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=text,
                                    reply_markup=btn)
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        logging.error(err)