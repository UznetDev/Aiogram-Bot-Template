from bot.loader import FM

from . import users

# error_handler
if FM.feature('error_handler'):
    from .errors import error_handler

# admin_panel
if FM.feature('admin_panel'):
    from . import admins

