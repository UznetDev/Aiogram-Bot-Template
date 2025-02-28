import logging
from aiogram import types
from aiogram.filters import CommandStart
from function.translator import translator
from loader import dp, bot, db
from keyboards.inline.user import send_url


@dp.message(CommandStart())
async def start_handler(msg: types.Message):
    """
    Handles the /start command by sending a greeting message and a button
    for sharing the bot's URL. Also logs the user if they are not already in the database.

    Args:
        msg (types.Message): The incoming message object.

    Returns:
        None
    """
    try:
        # User and bot information
        user_id = msg.from_user.id
        user_language = msg.from_user.language_code
        bot_info = await bot.get_me()
        bot_username = bot_info.username

        # Prepare the greeting text
        greeting_text = f'👋 Hello dear {bot_username}\n'

        # Translate the sharing message
        sharing_message = translator(text='I found a great bot, give it a try\n',
                                     dest=user_language)

        # Create the share button
        share_button = send_url(url=f'{sharing_message} https://t.me/{bot_username}?start',
                                language_code=user_language)

        # Translate and personalize the greeting text
        translated_greeting = translator(text=greeting_text, dest=user_language)

        # Send the greeting and share button
        await msg.answer(translated_greeting, reply_markup=share_button)

    except Exception as err:
        logging.error(f"Error handling /start command: {err}")
