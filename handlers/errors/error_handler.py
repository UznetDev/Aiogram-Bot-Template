import logging
import asyncio
from aiohttp import ClientError
from aiogram import Router
from aiogram.types import ErrorEvent, Update
from aiogram import Bot                  # for optional admin notification
from aiogram.exceptions import (
    TelegramBadRequest, TelegramRetryAfter, TelegramAPIError,
    TelegramUnauthorizedError, TelegramForbiddenError
    # (In aiogram v3.18, specific errors like "MessageNotModified" are categorized under TelegramBadRequest)
)
from loader import root_logger
# from data.config import ADMINS  # your admin IDs


router = Router()  # your main router

@router.errors()
async def global_error_handler(error: ErrorEvent) -> bool:
    """Global error handler for all exceptions in handlers."""
    update: Update = error.update
    exception = error.exception  # The actual exception object

    # 1. Message not modified (editing message with no changes)
    if isinstance(exception, TelegramBadRequest) and "message is not modified" in str(exception).lower():
        root_logger.info(f"Ignoring MessageNotModified error: {exception}")
        # No changes needed, so we simply ignore this error.
        return True  # Error handled

    # 2. Flood control: too many requests (429 error)
    elif isinstance(exception, TelegramRetryAfter):
        retry_after = exception.retry_after  # seconds to wait&#8203;:contentReference[oaicite:2]{index=2}
        root_logger.warning(f"Rate limit hit. Retrying after {retry_after} seconds.")
        await asyncio.sleep(retry_after)  # Wait required time before continuing
        # (Optionally, you might re-run the failed operation here if possible)
        return True  # Handled by waiting, no further propagation

    # 3. Unauthorized errors (e.g. invalid bot token or bot blocked)&#8203;:contentReference[oaicite:3]{index=3}&#8203;:contentReference[oaicite:4]{index=4}
    elif isinstance(exception, TelegramUnauthorizedError):
        root_logger.critical(f"Unauthorized: {exception} – Bot may have an invalid token.")
        # This is critical; the bot cannot operate if token is invalid.
        # (Optional) Notify admin about the issue if possible:
        # try:
        #     await Bot.get_current().send_message(ADMIN_CHAT_ID, f"CRITICAL: Bot unauthorized!\n{exception}")
        # except Exception:
        #     logger.error("Failed to notify admin about Unauthorized error.")
        return True
    elif isinstance(exception, TelegramForbiddenError):
        root_logger.error(f"Forbidden: {exception} – Bot lacks permission or was blocked in a chat.")
        # The bot was probably removed or blocked in the target chat.
        # We log this and proceed (no retry, as the action is not allowed).
        return True

    # 4. Bad Request errors (400 errors)&#8203;:contentReference[oaicite:5]{index=5}
    elif isinstance(exception, TelegramBadRequest):
        root_logger.error(f"BadRequest: {exception} – Update: {repr(update)}")
        # These indicate invalid requests (e.g. message not found, invalid parameters).
        # They are not critical for the bot's operation, so we log and mark as handled.
        return True

    # 5. General Telegram API errors (other errors from Telegram API)&#8203;:contentReference[oaicite:6]{index=6}
    elif isinstance(exception, TelegramAPIError):
        root_logger.error(f"TelegramAPIError: {exception}", exc_info=True)
        # This catches any other API error (e.g. server errors, timeouts wrapped by aiogram).
        # We log the full stack trace for debugging.
        # (Optional) Send notification to admin for critical API errors:
        # try:
        #     await Bot.get_current().send_message(ADMIN_CHAT_ID, f"⚠️ Telegram API error:\n{exception}")
        # except Exception as notify_err:
        #     logger.error(f"Failed to notify admin: {notify_err}")
        return True

    # 6. Network errors (aiohttp client errors, e.g. connectivity issues)
    elif isinstance(exception, ClientError):
        root_logger.error(f"NetworkError: {exception} – Possible network connectivity issue.")
        # These errors come from the HTTP client (aiohttp). Aiogram may raise them directly if TelegramNetworkError isn't used.
        # We log them and potentially attempt reconnection or alert an admin.
        return True

    # 7. Unhandled exceptions (any other type)
    else:
        root_logger.exception(f"Unhandled exception: {exception}")  # logs stack trace
        # You might want to notify an admin here as well, since this is unexpected.
        return True  # Mark as handled to prevent further propagation
