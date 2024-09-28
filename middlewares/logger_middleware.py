# middlewares/logger_middleware.py

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update
import logging
from utils.logger_adapter import ChatLoggerAdapter

class LoggerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        chat_id = None
        language_code = None

        if event.message:
            chat_id = event.message.chat.id
            language_code = event.message.from_user.language_code
        elif event.callback_query:
            chat_id = event.callback_query.message.chat.id
            language_code = event.callback_query.from_user.language_code
        elif event.inline_query:
            chat_id = event.inline_query.from_user.id
            language_code = event.inline_query.from_user.language_code
        elif event.chosen_inline_result:
            chat_id = event.chosen_inline_result.from_user.id
            language_code = event.chosen_inline_result.from_user.language_code

        # Create a logger adapter and add it to data
        data['logger'] = ChatLoggerAdapter(logging.getLogger(__name__), {
            'chat_id': chat_id,
            'language_code': language_code
        })

        return await handler(event, data)
