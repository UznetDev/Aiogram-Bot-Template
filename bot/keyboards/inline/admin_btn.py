from aiogram.utils.keyboard import InlineKeyboardBuilder

from .button import AdminCallback, EditAdminSetting, AdminSetting, BlockUser
from .close_btn import close_btn

from bot.data.config import ADMIN
from bot.loader import db, bot, translator, root_logger, FM, AM, SM
from bot.function.function import x_or_y


def main_btn():
    try:
        btn = InlineKeyboardBuilder()
        btn.button(text=f'🏠Main!',
                   callback_data=AdminCallback(action="main_adm_panel", data="").pack())
        return btn.as_markup()
    except Exception as err:
        root_logger.error(err)
        return False


def main_admin_panel_btn(user_id, language_code):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        rights = AM.list_features()
        for right in rights:
            if AM.__call__(user_id=user_id, feature=right['key']):
                text = translator(text=right['name'],
                                    dest=language_code)
                btn.button(text=text,
                            callback_data=AdminCallback(action=right['key'], data="").pack())
                    
        btn.adjust(1, 2)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        root_logger.error(err)
        return False

async def admin_setting(user_id, language_code):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        admins = AM.my_admins(user_id=user_id)
        for x in admins:
            info = await bot.get_chat(chat_id=x['user_id'])
            btn.button(text=f"{x_or_y(x['is_active'])} @{info.username}: {info.full_name}!",
                        callback_data=AdminSetting(action="attach_admin", user_id=x['user_id']).pack())
        btn.button(text=translator(text=f"👮‍♂️ ADD Admin!",
                                   dest=language_code),
                   callback_data=AdminCallback(action="add_admin", data="").pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        root_logger.error(err)
        return False

def attach_admin_btn(user_id, language_code):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))

        rights = AM.list_features()
        for right in rights:
            check = AM(user_id=user_id, feature=right['key'])
            text = x_or_y(check) + ' ' + translator(text=right['name'],
                                dest=language_code)
            
            btn.button(text=text,
                        callback_data=EditAdminSetting(
                            action="edit", 
                            user_id=user_id, 
                            data=right['key']).pack())
   
        btn.button(text=translator(text=f"🔪Delete admin!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='delete_admin').pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        root_logger.error(err)
        return False

def channel_settings(language_code):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        mandatory_membership = SM('mandatory_membership')
        if mandatory_membership == 'True':
            text = translator(text=f'✅ Mandatory membership of',
                              dest=language_code)
        else:
            text = translator(text=f'☑️ Mandatory membership on',
                              dest=language_code)
        btn.button(text=text,
                   callback_data=AdminCallback(action="mandatory_membership", data="").pack())
        btn.button(text=translator(text=f"➕ Add channel!",
                                   dest=language_code),
                   callback_data=AdminCallback(action="add_channel", data="").pack())

        btn.button(text=translator(text=f"➖ Remove Channel",
                                   dest=language_code),
                   callback_data=AdminCallback(action="remove_channel", data="").pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        root_logger.error(err)
        return False

def block_user(attention_user_id, language_code, user_id):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))

        if AM('block_user', user_id):
            data = db.check_user_ban(user_id=attention_user_id)
            if data is None:
                btn.button(text=translator(text=f"🚫Block user!",
                                           dest=language_code),
                           callback_data=BlockUser(action="block", user_id=attention_user_id).pack())
            else:
                if (data['initiator_user_id'] == user_id or data['updater_user_id'] == user_id) or user_id == ADMIN:
                    btn.button(text=translator(text=f"✅Unblock user!",
                                               dest=language_code),
                               callback_data=BlockUser(action="block", user_id=attention_user_id).pack())
        btn.adjust(1, 2)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        root_logger.error(err)
        return False

def download_statistika(user_id, language_code):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        if AM('view_statistika', user_id):
            btn.button(text=translator(text=f"📜 Dowload statistika!",
                                       dest=language_code),
                       callback_data=AdminCallback(action="download_statistika", data="").pack())
        btn.adjust(1, 2)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        root_logger.error(err)
        return False

def stop_advertisement():
    try:
        btn = InlineKeyboardBuilder()


        btn.button(
            text='🚫 Stop!',
            callback_data=AdminCallback(action="stop_ads", data="").pack()
        )

        return btn.as_markup()

    except Exception as err:
        root_logger.error(f"Error in stop_ads function: {err}")
        return False
