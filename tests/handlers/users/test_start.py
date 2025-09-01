# import pytest
# from bot.handlers.users.start import start_handler

# from aiogram_tests import MockedBot
# from aiogram_tests.handler import MessageHandler
# from aiogram_tests.types.dataset import MESSAGE


# @pytest.mark.asyncio
# async def test_echo():
#     request = MockedBot(MessageHandler(start_handler))
#     calls = await request.query(message=MESSAGE.as_object(text="Hello, Bot!"))
#     answer_message = calls.send_messsage.fetchone()
#     assert answer_message.text == "Hello, Bot!"
