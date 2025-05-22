from aiogram.utils.keyboard import InlineKeyboardBuilder

from .button import AdminCallback, EditAdminSetting, AdminSetting, BlockUser
from .close_btn import close_btn

from bot.data.config import ADMIN
from bot.loader import db, bot, translator, FM, root_logger
from bot.function.function import x_or_y
from bot.filters.admin import SelectAdmin


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

        is_admin = SelectAdmin(user_id=user_id)
        if is_admin.add_admin() and FM.feature('admin_settings'):
            btn.button(text=translator(text=f"👮‍♂️ Admins settings!",
                                       dest=language_code),
                       callback_data=AdminCallback(action="admin_settings", data="").pack())
        if is_admin.send_message():
            btn.button(text=translator(text=f"✈Send advertisement!",
                                       dest=language_code),
                       callback_data=AdminCallback(action="send_advertisement", data="").pack())
        if is_admin.view_statistika():
            btn.button(text=translator(text=f"📜Statistika!",
                                       dest=language_code),
                       callback_data=AdminCallback(action="statistika", data="").pack())
        if is_admin.block_user():
            btn.button(text=translator(text=f"👁‍🗨Check user!",
                                       dest=language_code),
                       callback_data=AdminCallback(action="check_user", data="").pack())
        if is_admin.channel_settings():
            btn.button(text=translator(text=f"🔰Channel setting!",
                                       dest=language_code),
                       callback_data=AdminCallback(action="channel_setting", data="").pack())
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
        if user_id == ADMIN:
            data = db.select_all_admins()
        else:
            data = db.select_add_admin(user_id=user_id)
        if data is not None:
            for x in data:
                info = await bot.get_chat(chat_id=x['user_id'])
                btn.button(text=f"👮‍♂️ @{info.username}: {info.full_name}!",
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


def attach_admin(user_id, language_code):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        is_admin = SelectAdmin(user_id=user_id)
        send_message_tx = x_or_y(is_admin.send_message())
        wiew_statistika_tx = x_or_y(is_admin.view_statistika())
        download_statistika_tx = x_or_y(is_admin.download_statistika())
        block_user_tx = x_or_y(is_admin.block_user())
        channel_settings_tx = x_or_y(is_admin.channel_settings())
        add_admin_tx = x_or_y(is_admin.add_admin())
        btn.button(text=translator(text=f"{send_message_tx} Send a message!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='send_message').pack())

        btn.button(text=translator(text=f"{wiew_statistika_tx} Wiew statistics!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='statistika').pack())

        btn.button(text=translator(text=f"{download_statistika_tx} Download statistics!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='download_statistika').pack())

        btn.button(text=translator(text=f"{block_user_tx} Block user!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='block_user').pack())
        btn.button(text=translator(text=f"{channel_settings_tx} Channel settings!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='channel_settings').pack())
        btn.button(text=translator(text=f"{add_admin_tx} Add a admin!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='add_admin').pack())
        btn.button(text=translator(text=f"🔪Delete admin!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='delete_admin').pack())
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
        is_admin = SelectAdmin(user_id=user_id)
        send_message_tx = x_or_y(is_admin.send_message())
        wiew_statistika_tx = x_or_y(is_admin.view_statistika())
        download_statistika_tx = x_or_y(is_admin.download_statistika())
        block_user_tx = x_or_y(is_admin.block_user())
        channel_settings_tx = x_or_y(is_admin.channel_settings())
        add_admin_tx = x_or_y(is_admin.add_admin())
        btn.button(text=translator(text=f"{send_message_tx} Send a message!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='send_message').pack())

        btn.button(text=translator(text=f"{wiew_statistika_tx} Wiew statistics!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='statistika').pack())

        btn.button(text=translator(text=f"{download_statistika_tx} Download statistics!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='download_statistika').pack())

        btn.button(text=translator(text=f"{block_user_tx} Block user!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='block_user').pack())
        btn.button(text=translator(text=f"{channel_settings_tx} Channel settings!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='channel_settings').pack())
        btn.button(text=translator(text=f"{add_admin_tx} Add a admin!",
                                   dest=language_code),
                   callback_data=EditAdminSetting(action="edit", user_id=user_id, data='add_admin').pack())
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
        mandatory_membership = db.select_setting('mandatory_membership')
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

        is_admin = SelectAdmin(user_id=user_id)
        if is_admin.block_user():
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
        is_admin = SelectAdmin(user_id=user_id)
        if is_admin.download_statistika():
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
        # Initialize the inline keyboard builder
        btn = InlineKeyboardBuilder()

        # Add a button labeled "🚫 Stop!" with callback data to handle the stop_ads action
        btn.button(
            text='🚫 Stop!',
            callback_data=AdminCallback(action="stop_ads", data="").pack()
        )

        # Return the constructed inline keyboard markup
        return btn.as_markup()

    except Exception as err:
        # Log any exceptions that occur during the button creation process
        root_logger.error(f"Error in stop_ads function: {err}")

        # Return False to indicate the failure of the operation
        return False
