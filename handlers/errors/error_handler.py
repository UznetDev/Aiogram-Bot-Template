import logging
from aiogram import types
from loader import dp
from aiogram.exceptions import (
    AiogramError,
    DetailedAiogramError,
    ClientDecodeError,
    SceneException,
    UnsupportedKeywordArgument,
    TelegramAPIError,
    TelegramNetworkError,
    TelegramRetryAfter,
    TelegramMigrateToChat,
    TelegramBadRequest,
    TelegramNotFound,
    TelegramConflictError,
    TelegramUnauthorizedError,
    TelegramForbiddenError,
    TelegramServerError,
    RestartingTelegram,
    TelegramEntityTooLarge
)

@dp.errors()
async def errors_handler(update: types.Update, exception: Exception):
    """
    Handles exceptions raised by Aiogram during task execution.

    :param update: The update that caused the exception.
    :param exception: The exception that was raised.
    :return: True if the exception was handled, otherwise False.
    """
    if isinstance(exception, (AiogramError, DetailedAiogramError, TelegramAPIError)):
        logging.exception('A Telegram API or Aiogram related error occurred.')
        return True
    elif isinstance(exception, ClientDecodeError):
        logging.exception("A client decode error occurred.")
        return True
    elif isinstance(exception, SceneException):
        logging.exception("An error occurred with scenes.")
        return True
    elif isinstance(exception, UnsupportedKeywordArgument):
        logging.exception("An unsupported keyword argument error occurred.")
        return True
    elif isinstance(exception, TelegramNetworkError):
        logging.exception("A network error occurred.")
        return True
    elif isinstance(exception, TelegramRetryAfter):
        logging.exception("Flood control exceeded. Retry after the specified time.")
        return True
    elif isinstance(exception, TelegramMigrateToChat):
        logging.exception("The chat has been migrated to a supergroup.")
        return True
    elif isinstance(exception, TelegramBadRequest):
        logging.exception("A malformed request error occurred.")
        return True
    elif isinstance(exception, TelegramNotFound):
        logging.exception("The requested resource was not found.")
        return True
    elif isinstance(exception, TelegramConflictError):
        logging.exception("A bot token conflict error occurred.")
        return True
    elif isinstance(exception, TelegramUnauthorizedError):
        logging.exception("An unauthorized bot token error occurred.")
        return True
    elif isinstance(exception, TelegramForbiddenError):
        logging.exception("The bot is forbidden from accessing the chat.")
        return True
    elif isinstance(exception, TelegramServerError):
        logging.exception("A Telegram server error (5xx) occurred.")
        return True
    elif isinstance(exception, RestartingTelegram):
        logging.exception("The Telegram server is restarting.")
        return True
    elif isinstance(exception, TelegramEntityTooLarge):
        logging.exception("The file size is too large to send.")
        return True
    else:
        logging.exception(f'An unhandled exception occurred: {exception}')
        return False
