import time
from aiogram import BaseMiddleware
from aiogram.types import Update
import logging
from utils.logger_adapter import ChatLoggerAdapter


class ExecutionTimeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Start the timer
        start_time = time.perf_counter()

        # Call the handler and get the result
        result = await handler(event, data)

        # End the timer
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Extract chat_id and language_code from the event
        chat_id = None
        language_code = None

        if event.message:
            chat_id = event.message.chat.id
            language_code = event.message.from_user.language_code
        elif event.callback_query:
            chat_id = event.callback_query.message.chat.id
            language_code = event.callback_query.from_user.language_code

        # Create a logger adapter and include execution_time in the extra data
        logger = ChatLoggerAdapter(logging.getLogger(__name__), {
            'chat_id': chat_id,
            'language_code': language_code,
            'execution_time': execution_time
        })

        # Log the execution time
        handler_name = handler.__name__ if hasattr(handler, '__name__') else str(handler)
        logger.info(f"Handler {handler_name} executed in {execution_time:.6f} seconds")

        return result
