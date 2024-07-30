import logging
from loader import dp
from aiogram.exceptions import (AiogramError,
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
                                TelegramEntityTooLarge,
                                ClientDecodeError)


@dp.errors()
async def errors_handler(update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param dispatcher:
    :param update:
    :param exception:
    :return: stdout logging and bool
    """
    if isinstance(exception, AiogramError):
        logging.exception('Aiogram error')
        return True
    elif isinstance(exception, DetailedAiogramError):
        logging.exception('Aiogram errors with detailed message.')
        return True
    elif isinstance(exception, ClientDecodeError):
        logging.exception("Exception for callback answer")
        return True
    elif isinstance(exception, SceneException):
        logging.exception("Exception for scenes.")
        return True
    elif isinstance(exception, UnsupportedKeywordArgument):
        logging.exception("Exception raised when a keyword argument is passed as filter.")
        return True
    elif isinstance(exception, TelegramAPIError):
        logging.exception("Base exception for all Telegram API errors.")
        return True
    elif isinstance(exception, TelegramNetworkError):
        logging.exception("Base exception for all Telegram network errors.")
        return True
    elif isinstance(exception, TelegramRetryAfter):
        logging.exception("Exception raised when flood control exceeds.")
        return True
    elif isinstance(exception, TelegramMigrateToChat):
        logging.exception("Exception raised when chat has been migrated to a supergroup.")
        return True
    elif isinstance(exception, TelegramBadRequest):
        logging.exception("Exception raised when request is malformed.")
        return True
    elif isinstance(exception, TelegramNotFound):
        logging.exception("Exception raised when chat, message, user, etc. not found.")
        return True
    elif isinstance(exception, TelegramConflictError):
        logging.exception("Exception raised when bot token is already used by another application in polling mode.")
        return True
    elif isinstance(exception, TelegramUnauthorizedError):
        logging.exception("Exception raised when bot token is invalid.")
        return True
    elif isinstance(exception, TelegramForbiddenError):
        logging.exception("Exception raised when bot is kicked from chat or etc.")
        return True
    elif isinstance(exception, TelegramServerError):
        logging.exception("Exception raised when Telegram server returns 5xx error.")
        return True
    elif isinstance(exception, RestartingTelegram):
        logging.exception("Exception raised when Telegram server is restarting.")
        return True
    elif isinstance(exception, TelegramEntityTooLarge):
        logging.exception("Exception raised when you are trying to send a file that is too large.")
        return True
    elif isinstance(exception, ClientDecodeError):
        logging.exception("Exception raised when client can’t decode response.")
    else:
        logging.exception(f'Update: {update} \n{exception}')