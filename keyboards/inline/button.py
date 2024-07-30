from aiogram.filters.callback_data import CallbackData


class MainCallback(CallbackData, prefix="m"):
    action: str
    q: str


class AdminCallback(CallbackData, prefix="admin"):
    action: str
    data: str


class EditAdminSetting(CallbackData, prefix="edit_setting"):
    action: str
    cid: int
    data: str

class AdminSetting(CallbackData, prefix="admin_setting"):
    action: str
    cid: int


class BlockUser(CallbackData, prefix="block_user"):
    action: str
    cid: int