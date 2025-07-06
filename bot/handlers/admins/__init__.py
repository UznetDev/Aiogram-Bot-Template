from bot.loader import FM


from . import main_panel
from . import super_admin
from .callback_query import main_admin_panel


# admin_settings
if FM.feature('admin_settings'):
    from . import admin_settings

# statistika
if FM.feature('statistika'):
    from . import statistika