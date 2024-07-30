import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from function.translator import translator


def send_url(url, lang):
    """
    Creates an inline keyboard with a button to share a URL.

    Args:
        url (str): The URL to be shared.
        lang (str): The language code for translation.

    Returns:
        aiogram.types.InlineKeyboardMarkup: The markup for the inline keyboard with the share button,
        or False if an error occurred.
    """
    try:
        btn = InlineKeyboardBuilder()
        btn.button(
            text=translator(text='➕Share to friend', dest=lang),
            url=f'https://t.me/share/url?url={url}'
        )
        btn.adjust(1)
        return btn.as_markup()
    except Exception as err:
        logging.error(f"Error creating URL share button: {err}")
        return False


def share_audio(text: str, lang):
    """
    Creates an inline keyboard with a button to share audio content via an inline query.

    Args:
        text (str): The text to be shared in the inline query.
        lang (str): The language code for translation.

    Returns:
        aiogram.types.InlineKeyboardMarkup: The markup for the inline keyboard with the share button,
        or False if an error occurred.
    """
    try:
        btn = InlineKeyboardBuilder()
        text = text.strip()
        btn.button(
            text=translator(text='➕Share to friend', dest=lang),
            switch_inline_query=text
        )
        btn.adjust(1)
        return btn.as_markup()
    except Exception as err:
        logging.error(f"Error creating audio share button: {err}")
        return False

