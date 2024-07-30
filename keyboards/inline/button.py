from aiogram.filters.callback_data import CallbackData

class MainCallback(CallbackData, prefix="m"):
    """
    Handles callback queries for main actions.

    Attributes:
        action (str): The specific action to be performed.
        q (str): An optional query parameter for additional data.
    """
    action: str
    q: str

class AdminCallback(CallbackData, prefix="admin"):
    """
    Handles callback queries for admin-related actions.

    Attributes:
        action (str): The specific admin action to be performed.
        data (str): Data related to the admin action.
    """
    action: str
    data: str

class EditAdminSetting(CallbackData, prefix="edit_setting"):
    """
    Handles callback queries for editing admin settings.

    Attributes:
        action (str): The specific action to be performed on settings.
        cid (int): The ID of the admin or user related to the setting.
        data (str): The specific setting to be edited.
    """
    action: str
    cid: int
    data: str

class AdminSetting(CallbackData, prefix="admin_setting"):
    """
    Handles callback queries for admin settings actions.

    Attributes:
        action (str): The specific action related to admin settings.
        cid (int): The ID of the admin or user related to the setting.
    """
    action: str
    cid: int

class BlockUser(CallbackData, prefix="block_user"):
    """
    Handles callback queries for blocking or unblocking users.

    Attributes:
        action (str): The specific action to be performed (block/unblock).
        cid (int): The ID of the user to be blocked or unblocked.
    """
    action: str
    cid: int
