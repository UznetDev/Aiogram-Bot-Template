from bot.loader import FM


from . import main_panel
from . import super_admin

# admin_settings
if FM.feature('admin_settings'):
    from . import admin_settings