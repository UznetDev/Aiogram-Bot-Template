from aiogram import types
from loader import bot

async def set_default_commands():
    await bot.set_my_commands(
        [
            types.BotCommand(command='start', description='♻Start bot..'),
            types.BotCommand(command='help', description='📜Help and Information..'),
            types.BotCommand(command='my', description='📻Your playlist..')
        ]
    )
