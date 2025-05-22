from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.data.config import ADMIN
from bot.loader import db


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
        self.dada = db.select_admin(user_id=self.user_id)
        if self.user_id == ADMIN:
            return True
        elif self.dada is not None:
            return True
        else:
            return False


class SelectAdmin:

    def __init__(self, user_id):
        self.user_id = user_id
        self.super_admin = ADMIN
        self.dada = db.select_admin(user_id=self.user_id)

    def send_message(self) -> bool:
        if self.user_id == self.super_admin:
            return True
        elif self.dada['send_message'] == 1:
            return True
        else:
            return False

    def view_statistika(self) -> bool:
        if self.user_id == self.super_admin:
            return True
        elif self.dada['statistika'] == 1:
            return True
        else:
            return False

    def download_statistika(self) -> bool:
        if self.user_id == self.super_admin:
            return True
        elif self.dada['download_statistika'] == 1:
            return True
        else:
            return False

    def block_user(self) -> bool:
        if self.user_id == self.super_admin:
            return True
        elif self.dada['block_user'] == 1:
            return True
        else:
            return False

    def channel_settings(self) -> bool:
        if self.user_id == self.super_admin:
            return True
        elif self.dada['channel_settings'] == 1:
            return True
        else:
            return False

    def add_admin(self) -> bool:
        if self.user_id == self.super_admin:
            return True
        elif self.dada['add_admin'] == 1:
            return True
        else:
            return False