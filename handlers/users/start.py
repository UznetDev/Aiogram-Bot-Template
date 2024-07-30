import logging
from aiogram import types
from aiogram.filters import CommandStart
from function.translator import translator
from loader import *
from data.config import yil_oy_kun, soat_minut_sekund
from keyboards.inline.user import send_url


@dp.message(CommandStart())
async def start_handler(msg: types.Message):
    try:
        cid = msg.from_user.id
        lang = msg.from_user.language_code
        bot_info = await bot.get_me()
        bot_username = bot_info.username

        text = f'👋Hello dear %s\n'

        tx = translator(text=f'I found a great bot, give it a try\n',
                        dest=lang)

        btn = send_url(url=f'{tx} https://t.me/{bot_username}?start',
                       lang=lang)
        tr_text = translator(text=text,
                             dest=lang)
        tr_text = tr_text % (bot_username, )
        await msg.answer(tr_text,
                         reply_markup=btn)
        if db.check_user(cid=cid) is None:
            db.add_user(cid=cid,
                        date=str(yil_oy_kun) + ' / ' + str(soat_minut_sekund),
                        lang=lang)
    except Exception as err:
        logging.error(err)
