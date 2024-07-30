import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.admin_btn import channel_settings
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from data.config import ADMIN


@dp.callback_query(AdminCallback.filter(F.action == "channel_setting"), IsAdmin())
async def channel_setting(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        btn = close_btn()
        if data.channel_settings():
            if cid == ADMIN:
                data = db.select_channels()
            else:
                data = db.select_channels_add_cid(add_cid=cid)
            if not data:
                text = translator(text="❔ The channel list is empty!\n\n",
                                  dest=lang)
            else:
                text = translator(text="🔰 List of channels:\n\n",
                                  dest=lang)
                count = 0
                for x in data:
                    try:
                        count += 1
                        chat_id = str(-100) + str(x[1])
                        channel = await bot.get_chat(chat_id=chat_id)
                        text += (f"<b><i>{count}</i>. Name:</b> <i>{channel.full_name}</i>\n"
                                 f"<b>Username:</b> <i>@{channel.username}\n</i>"
                                 f"<b>Added date:</b> <i>{x[3]}\n</i>"
                                 f"<b>Added by CID:</b> <i>{x[2]}\n\n</i>")
                    except Exception as err:
                        logging.error(err)
            btn = channel_settings(lang=lang)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!',
                              dest=lang)
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        logging.error(err)
