import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from function.translator import translator


def send_url(url, lang):
    try:
        btn = InlineKeyboardBuilder()
        btn.button(text=translator(text='➕Share to friend',
                                   dest=lang),
                   url=f'https://t.me/share/url?url={url}')
        btn.adjust(1)
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def share_audio(text: str, lang):
    try:
        btn = InlineKeyboardBuilder()
        text = text.strip()
        btn.button(text=translator(text='➕Share to friend',
                                   dest=lang),
                   switch_inline_query=text)
        btn.adjust(1)
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False