import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.config import ADMIN
from loader import db

class IsBan(BaseFilter):
    def __init__(self):
        self.super_admin = ADMIN
    async def __call__(self, message: Message) -> bool:
        try:
            self.cid = message.from_user.id
            self.dada = db.select_admin(cid=self.cid)
            check_ban = db.check_user_ban(cid=self.cid)
            if self.cid ==  self.super_admin:
                return False
            elif self.dada is not None:
                return False
            elif check_ban is None:
                return False
            else:
                return True
        except Exception as err:
            logging.error(err)
            return False