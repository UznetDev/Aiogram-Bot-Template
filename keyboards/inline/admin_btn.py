import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .button import AdminCallback, EditAdminSetting, AdminSetting, BlockUser
from .close_btn import close_btn
from function.translator import translator
from filters.admin import SelectAdmin
from data.config import ADMIN
from loader import db, bot, DB
from function.function import x_or_y


def main_btn():
    """
    Creates the main button for the admin panel.

    Returns:
        InlineKeyboardMarkup: The markup for the main button.
        False: Returns False if an error occurs.

    This function creates a button with the text '🏠Main!' and attaches a callback
    action to navigate to the main admin panel.
    """
    try:
        btn = InlineKeyboardBuilder()
        btn.button(text=f'🏠Main!',
                   callback_data=AdminCallback(action="main_adm_panel", data="").pack())
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def main_admin_panel_btn(cid, lang):
    """
    Creates the inline keyboard for the main admin panel.

    Parameters:
        cid (int): The ID of the current user.
        lang (str): The language code for translation.

    Returns:
        InlineKeyboardMarkup: The markup for the main admin panel buttons.
        False: Returns False if an error occurs.

    This function creates buttons for various admin actions based on the permissions
    of the current user. Includes settings for admins, sending advertisements, viewing
    statistics, checking users, and channel settings.
    """
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
        if is_admin.view_statistika():
            btn.button(text=translator(text=f"📜Statistika!",
                                       dest=lang),
                       callback_data=AdminCallback(action="statistika", data="").pack())
        if is_admin.block_user():
            btn.button(text=translator(text=f"👁‍🗨Check user!",
                                       dest=lang),
                       callback_data=AdminCallback(action="check_user", data="").pack())
        if is_admin.channel_settings():
            btn.button(text=translator(text=f"🔰Channel setting!",
                                       dest=lang),
                       callback_data=AdminCallback(action="channel_setting", data="").pack())
        btn.adjust(1, 2)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


async def admin_setting(cid, lang):
    """
    Creates the inline keyboard for admin settings.

    Parameters:
        cid (int): The ID of the current user.
        lang (str): The language code for translation.

    Returns:
        InlineKeyboardMarkup: The markup for admin settings buttons.
        False: Returns False if an error occurs.

    This function creates a button for each existing admin and an option to add a new admin.
    It lists all admins if the current user is the main admin or only relevant admins otherwise.
    """
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
    """
    Creates the inline keyboard for managing admin settings.

    Parameters:
        cid (int): The ID of the current user.
        lang (str): The language code for translation.

    Returns:
        InlineKeyboardMarkup: The markup for admin settings management buttons.
        False: Returns False if an error occurs.

    This function creates buttons for each admin setting, allowing modifications
    for sending messages, viewing statistics, downloading statistics, blocking users,
    channel settings, adding, and deleting admins.
    """
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        is_admin = SelectAdmin(cid=cid)
        send_message_tx = x_or_y(is_admin.send_message())
        wiew_statistika_tx = x_or_y(is_admin.view_statistika())
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
    """
    Creates the inline keyboard for managing admin settings.

    Parameters:
        cid (int): The ID of the current user.
        lang (str): The language code for translation.

    Returns:
        InlineKeyboardMarkup: The markup for admin settings management buttons.
        False: Returns False if an error occurs.

    This function is similar to `attach_admin` but may serve a slightly different purpose
    in the application. It allows the modification of admin settings such as sending
    messages, viewing and downloading statistics, blocking users, channel settings,
    adding, and deleting admins.
    """
    try:
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))
        is_admin = SelectAdmin(cid=cid)
        send_message_tx = x_or_y(is_admin.send_message())
        wiew_statistika_tx = x_or_y(is_admin.view_statistika())
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
    """
    Creates the inline keyboard for channel settings.

    Parameters:
        lang (str): The language code for translation.

    Returns:
        InlineKeyboardMarkup: The markup for channel settings buttons.
        False: Returns False if an error occurs.

    This function creates buttons to configure channel settings, including adding,
    removing channels, and setting mandatory membership requirements.
    """
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
                   callback_data=AdminCallback(action="add_channel", data="").pack())

        btn.button(text=translator(text=f"➖ Remove Channel",
                                   dest=lang),
                   callback_data=AdminCallback(action="remove_channel", data="").pack())
        btn.adjust(1)
        btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        return btn.as_markup()
    except Exception as err:
        logging.error(err)
        return False


def block_user(cid, lang, user_id):
    """
    Creates the inline keyboard for blocking or unblocking a user.

    Parameters:
        cid (int): The ID of the current user.
        lang (str): The language code for translation.
        user_id (int): The ID of the user to be blocked or unblocked.

    Returns:
        InlineKeyboardMarkup: The markup for block/unblock user buttons.
        False: Returns False if an error occurs.

    This function creates a button to either block or unblock a user, depending on their
    current status. If the user is not banned, it offers to block them; if they are banned,
    it offers to unblock them.
    """
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
    """
    Creates the inline keyboard for downloading statistics.

    Parameters:
        cid (int): The ID of the current user.
        lang (str): The language code for translation.

    Returns:
        InlineKeyboardMarkup: The markup for download statistics button.
        False: Returns False if an error occurs.

    This function creates a button for downloading statistics if the current user has
    the permission to do so.
    """
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


def stop_advertisement():
    """
    Creates an inline keyboard with a single "🚫 Stop!" button for stopping advertisements.

    This function utilizes the `InlineKeyboardBuilder` to construct an inline keyboard with a button
    labeled "🚫 Stop!". The button's callback data is generated using the `AdminCallback` class,
    specifying the action "stop_ads". This callback data is used by the bot to handle the button
    press event appropriately.

    The function is wrapped in a try-except block to catch any exceptions that may occur during
    the creation of the inline keyboard. If an exception is raised, the error is logged, and the
    function returns `False` to indicate that the operation failed.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup object containing the "🚫 Stop!" button,
                              if successfully created.
        bool: Returns `False` if an exception occurs during the creation process.

    Exceptions:
        If an exception is encountered, it is caught and logged using the logging module, with
        an error message indicating the source of the error.

    Example Usage:
        To create an inline keyboard for stopping ads:

        keyboard = stop_ads()
        if keyboard:
            await message.reply("Press the button to stop ads.", reply_markup=keyboard)
        else:
            await message.reply("Failed to create stop button.")
    """
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
        logging.error(f"Error in stop_ads function: {err}")

        # Return False to indicate the failure of the operation
        return False
