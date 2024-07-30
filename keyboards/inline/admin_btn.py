import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .button import AdminCallback, EditAdminSetting, AdminSetting, BlockUser
from .close_btn import close_btn
from function.translator import translator
from filters.admin import SelectAdmin
from data.config import ADMIN, DB
from loader import db, bot
from function.function import x_or_y


def main_btn():
    try:
        btn = InlineKeyboardBuilder()
        btn.button(text=f'🏠Main!',
                   callback_data=AdminCallback(action="main_adm_panel", data="").pack())
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def main_admin_panel_btn(cid, lang):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))

        is_admin = SelectAdmin(cid=cid)
        if is_admin.add_admin():
            btn.button(text=translator(text=f"👮‍♂️ Admins settings!",
                                       dest=lang),
                       callback_data=AdminCallback(action="admin_settings", data="").pack())
        if is_admin.send_message():
            btn.button(text=translator(text=f"✈Send advertisement!",
                                       dest=lang),
                       callback_data=AdminCallback(action="send_advertisement", data="").pack())
        if is_admin.wiew_statistika():
            btn.button(text=translator(text=f"📜Statistika!",
                                       dest=lang),
                       callback_data=AdminCallback(action="statistika", data="").pack())
        if is_admin.block_user():
            btn.button(text=translator(text=f"👁‍🗨Check user!",
                                       dest=lang),
                       callback_data=AdminCallback(action="check_user", data="").pack())
        if is_admin.channel_settings():
            btn.button(text=translator(text=f"🔰Channel settingr!",
                                       dest=lang),
                       callback_data=AdminCallback(action="channel_setting", data="").pack())
        btn.adjust(1, 2)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


async def admin_setting(cid, lang):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        if cid == ADMIN:
            data = db.select_all_admins()
        else:
            data = db.select_add_admin(cid=cid)
        if data is not None:
            for x in data:
                info = await bot.get_chat(chat_id=x[1])
                btn.button(text=f"👮‍♂️ @{info.username}: {info.full_name}!",
                           callback_data=AdminSetting(action="attach_admin", cid=x[1]).pack())
        btn.button(text=translator(text=f"👮‍♂️ ADD Admin!",
                                   dest=lang),
                   callback_data=AdminCallback(action="add_admin", data="").pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def attach_admin(cid, lang):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        is_admin = SelectAdmin(cid=cid)
        send_message_tx = x_or_y(is_admin.send_message())
        wiew_statistika_tx = x_or_y(is_admin.wiew_statistika())
        download_statistika_tx = x_or_y(is_admin.download_statistika())
        block_user_tx = x_or_y(is_admin.block_user())
        channel_settings_tx = x_or_y(is_admin.channel_settings())
        add_admin_tx = x_or_y(is_admin.add_admin())
        btn.button(text=translator(text=f"{send_message_tx} Send a message!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='send_message').pack())

        btn.button(text=translator(text=f"{wiew_statistika_tx} Wiew statistics!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='statistika').pack())

        btn.button(text=translator(text=f"{download_statistika_tx} Download statistics!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='download_statistika').pack())

        btn.button(text=translator(text=f"{block_user_tx} Block user!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='block_user').pack())
        btn.button(text=translator(text=f"{channel_settings_tx} Channel settings!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='channel_settings').pack())
        btn.button(text=translator(text=f"{add_admin_tx} Add a admin!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='add_admin').pack())
        btn.button(text=translator(text=f"🔪Delete admin!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='delete_admin').pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def attach_admin_btn(cid, lang):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        is_admin = SelectAdmin(cid=cid)
        send_message_tx = x_or_y(is_admin.send_message())
        wiew_statistika_tx = x_or_y(is_admin.wiew_statistika())
        download_statistika_tx = x_or_y(is_admin.download_statistika())
        block_user_tx = x_or_y(is_admin.block_user())
        channel_settings_tx = x_or_y(is_admin.channel_settings())
        add_admin_tx = x_or_y(is_admin.add_admin())
        btn.button(text=translator(text=f"{send_message_tx} Send a message!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='send_message').pack())

        btn.button(text=translator(text=f"{wiew_statistika_tx} Wiew statistics!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='statistika').pack())

        btn.button(text=translator(text=f"{download_statistika_tx} Download statistics!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='download_statistika').pack())

        btn.button(text=translator(text=f"{block_user_tx} Block user!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='block_user').pack())
        btn.button(text=translator(text=f"{channel_settings_tx} Channel settings!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='channel_settings').pack())
        btn.button(text=translator(text=f"{add_admin_tx} Add a admin!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='add_admin').pack())
        btn.button(text=translator(text=f"🔪Delete admin!",
                                   dest=lang),
                   callback_data=EditAdminSetting(action="edit", cid=cid, data='delete_admin').pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def channel_settings(lang):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        data = DB.reading_db()
        if data['join_channel']:
            text = translator(text=f'✅ Mandatory membership of',
                              dest=lang)
        else:
            text = translator(text=f'☑️ Mandatory membership on',
                              dest=lang)
        btn.button(text=text,
                   callback_data=AdminCallback(action="mandatory_membership", data="").pack())
        btn.button(text=translator(text=f"➕ Add channel!",
                                   dest=lang),
                   callback_data=AdminCallback(action="add_chanel", data="").pack())

        btn.button(text=translator(text=f"➖ Remove Channel",
                                   dest=lang),
                   callback_data=AdminCallback(action="remove_chanel", data="").pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def block_user(cid, lang, user_id):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))

        is_admin = SelectAdmin(cid=cid)
        if is_admin.block_user():
            data = db.check_user_ban(cid=user_id)
            if data is None:
                btn.button(text=translator(text=f"🚫Userni bloklash!",
                                           dest=lang),
                           callback_data=BlockUser(action="block", cid=user_id).pack())
            else:
                if data[2] == cid or cid == ADMIN:
                    btn.button(text=translator(text=f"✅Unblock user!",
                                               dest=lang),
                               callback_data=BlockUser(action="block", cid=user_id).pack())
        btn.adjust(1, 2)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def download_statistika(cid, lang):
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        is_admin = SelectAdmin(cid=cid)
        if is_admin.download_statistika():
            btn.button(text=translator(text=f"📜 Dowload statistika!",
                                       dest=lang),
                       callback_data=AdminCallback(action="download_statistika", data="").pack())
        btn.adjust(1, 2)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False