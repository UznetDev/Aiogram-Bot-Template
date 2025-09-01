from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import Optional, Any

from bot.data.config import ADMIN
from bot.loader import db, redis, AM


class IsSuperAdmin(BaseFilter):
    def __init__(self):
        self.ADMIN = ADMIN

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        if user_id == self.ADMIN:
            return True
        else:
            return False


class IsAdmin(BaseFilter):
    def __init__(self):
        self.ADMIN = ADMIN

    async def __call__(self, message: Message) -> bool:
        self.user_id = message.from_user.id
        is_admin, _, _, _ = AM.__getitem__(self.user_id)
        return True if is_admin  else False

