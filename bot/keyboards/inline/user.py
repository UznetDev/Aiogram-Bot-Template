import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.loader import translator


def send_url(language_code, url):
    try:
        btn = InlineKeyboardBuilder()
        btn.button(
            text=translator(text='➕Share to friend', dest=language_code),
            url=f'https://t.me/share/url?url={url}'
        )
        btn.adjust(1)
        return btn.as_markup()
    except Exception as err:
        logging.error(f"Error creating URL share button: {err}")
        return False


def share_audio(text: str, language_code):
    """
    Creates an inline keyboard with a button to share audio content via an inline query.

    Args:
        text (str): The text to be shared in the inline query.
        language_code (str): The language code for translation.

    Returns:
        aiogram.types.InlineKeyboardMarkup: The markup for the inline keyboard with the share button,
        or False if an error occurred.
    """
    try:
        btn = InlineKeyboardBuilder()
        text = text.strip()
        btn.button(
            text=translator(text='➕Share to friend', dest=language_code),
            switch_inline_query=text
        )
        btn.adjust(1)
        return btn.as_markup()
    except Exception as err:
        logging.error(f"Error creating audio share button: {err}")
        return False

