import logging

from aiogram import types
from aiogram.filters import Command
from function.translator import translator
from loader import dp, bot
from keyboards.inline.user import send_url


@dp.message(Command(commands='help'))
async def start_handler(msg: types.Message):
    try:
        lang = msg.from_user.language_code
        bot_info = await bot.get_me()
        text = "Same text for help"

        tx = translator(text=f'I found a great bot, give it a try.\n',
                        dest=lang)
        btn = send_url(url=f'{tx} https://t.me/{bot_info.username}?start',
                       lang=lang)
        text = translator(text=text,
                          dest=lang)
        await msg.answer(text,
                         reply_markup=btn)
    except Exception as err:
        logging.error(err)
