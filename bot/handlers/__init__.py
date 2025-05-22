from bot.loader import FM

from . import users

if FM.feature('error_handler'):
    from .errors import error_handler

