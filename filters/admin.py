from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.config import ADMIN
from loader import db


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
        self.cid = message.from_user.id
        self.dada = db.select_admin(cid=self.cid)
        if self.cid == ADMIN:
            return True
        elif self.dada is not None:
            return True
        else:
            return False


class SelectAdmin:
    def __init__(self, cid):
        self.cid = cid
        self.super_admin = ADMIN
        self.dada = db.select_admin(cid=self.cid)

    def send_message(self):
        if self.cid == self.super_admin:
            return True
        elif self.dada[3] == 1:
            return True
        else:
            return False

    def wiew_statistika(self):
        if self.cid == self.super_admin:
            return True
        elif self.dada[4] == 1:
            return True
        else:
            return False

    def download_statistika(self):
        if self.cid == self.super_admin:
            return True
        elif self.dada[5] == 1:
            return True
        else:
            return False

    def block_user(self):
        if self.cid == self.super_admin:
            return True
        elif self.dada[6] == 1:
            return True
        else:
            return False

    def channel_settings(self):
        if self.cid == self.super_admin:
            return True
        elif self.dada[7] == 1:
            return True
        else:
            return False

    def add_admin(self):
        if self.cid == self.super_admin:
            return True
        elif self.dada[8] == 1:
            return True
        else:
            return False
