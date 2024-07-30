import logging
from loader import dp,bot,db
from aiogram import types
from function.translator import translator
from keyboards.inline.close_btn import close_btn
from data.config import yil_oy_kun,soat_minut_sekund, ADMIN
from filters.ban import IsBan


@dp.message(IsBan())
async def start_handler(msg: types.Message):
    try:
        lang = msg.from_user.language_code
        cid = msg.from_user.id
        info = db.check_user_ban(cid=cid)
        logging.info(info)
        admin_info = await bot.get_chat(chat_id=info[2])
        admins = await bot.get_chat(chat_id=ADMIN)
        tx = f'<b>👩‍💻Super admin @{admins.username}</b>\n'
        text = translator(text="<b>🛑 You are banned!:\n</b>"
                               "<i>⚠If you think this is a mistake, contact the admin.</i>",
                          dest=lang)
        text = f'{text}' \
               f'\n\n<b>👮‍♂️Admin @{admin_info.username}</b>\n {tx}'
        await msg.answer(text=text,
                         reply_markup=close_btn())
        if db.check_user(cid=cid) is None:
            db.add_user(cid=cid,
                        date=str(yil_oy_kun) + ' / ' + str(soat_minut_sekund))
    except Exception as err:
        logging.error(err)