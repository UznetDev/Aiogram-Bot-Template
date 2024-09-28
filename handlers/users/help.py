import logging
import time
from aiogram import types
from aiogram.filters import Command
from function.translator import translator
from loader import dp, bot
from keyboards.inline.user import send_url


@dp.message(Command(commands='help'))
async def help_handler(msg: types.Message):
    """
    Handles the /help command to provide users with information about the bot
    and a button to share the bot's URL.

    Args:
        msg (types.Message): The incoming message object.

    Returns:
        None
    """
    start_time = time.perf_counter()
    try:
        # Get the user's language code
        user_language = msg.from_user.language_code

        user_id = msg.chat.id

        # Get information about the bot
        bot_info = await bot.get_me()

        # Define the help text
        help_text = "Same text for help"

        # Translate the sharing message
        sharing_message = translator(text='I found a great bot, give it a try.\n',
                                     dest=user_language)

        # Create a URL button for sharing the bot
        share_button = send_url(url=f'{sharing_message} https://t.me/{bot_info.username}?start',
                                lang=user_language)

        # Translate the help text
        translated_help_text = translator(text=help_text, dest=user_language)

        # Send the help text and button to the user
        await msg.answer(translated_help_text, reply_markup=share_button)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.info(f"Handling /help",
                     extra={
                         'chat_id': user_id,
                         'language_code': user_language,
                         'execution_time': execution_time
                     })
    except Exception as err:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.error(f"Error in /help handler: {err}",
                      extra={
                          'chat_id': user_id,
                          'language_code': user_language,
                          'execution_time': execution_time
                      })
