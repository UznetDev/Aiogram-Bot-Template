import logging
from aiogram import types
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
        logging.exception('Telegram API or Aiogram related error occurred.')
        return True
    elif isinstance(exception, ClientDecodeError):
        logging.exception("Client decode error occurred.")
        return True
    elif isinstance(exception, SceneException):
        logging.exception("Error occurred with scenes.")
        return True
    elif isinstance(exception, UnsupportedKeywordArgument):
        logging.exception("Unsupported keyword argument error occurred.")
        return True
    elif isinstance(exception, TelegramNetworkError):
        logging.exception("Network error occurred.")
        return True
    elif isinstance(exception, TelegramRetryAfter):
        logging.exception("Flood control exceeded. Retry after the specified time.")
        return True
    elif isinstance(exception, TelegramMigrateToChat):
        logging.exception("Chat has been migrated to a supergroup.")
        return True
    elif isinstance(exception, TelegramBadRequest):
        logging.exception("Malformed request error.")
        return True
    elif isinstance(exception, TelegramNotFound):
        logging.exception("Requested resource not found.")
        return True
    elif isinstance(exception, TelegramConflictError):
        logging.exception("Bot token conflict error.")
        return True
    elif isinstance(exception, TelegramUnauthorizedError):
        logging.exception("Unauthorized bot token error.")
        return True
    elif isinstance(exception, TelegramForbiddenError):
        logging.exception("Bot is forbidden from accessing the chat.")
        return True
    elif isinstance(exception, TelegramServerError):
        logging.exception("Telegram server error (5xx).")
        return True
    elif isinstance(exception, RestartingTelegram):
        logging.exception("Telegram server is restarting.")
        return True
    elif isinstance(exception, TelegramEntityTooLarge):
        logging.exception("File size is too large to send.")
        return True
    else:
        logging.exception(f'Unhandled exception occurred: {exception}')
        return False
