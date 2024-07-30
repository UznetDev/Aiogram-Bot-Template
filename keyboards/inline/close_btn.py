import logging
from .button import MainCallback
from aiogram.utils.keyboard import InlineKeyboardBuilder


def close_btn():
    try:
        btn = InlineKeyboardBuilder()
        btn.button(text='❌ Close',
                   callback_data=MainCallback(action="close", q="").pack())
        btn.adjust(1)
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False