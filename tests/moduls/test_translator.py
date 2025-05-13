import pytest
from bot.api.translator import Translator
from bot.loader import db
from bot.function.function import to_hash


@pytest.mark.asyncio
async def test_translator_no_feature(monkeypatch):
    class FM:
        def __init__(self, defoult_return: bool = True):
            self.defoult_return = defoult_return
        def feature(self, *args,**kwargs) : 
            return self.defoult_return

    tr = Translator(db=db, FM=FM(False))
    result = tr.translate("Hello", dest="fr", src="en")
    assert result == "Hello"

    tr = Translator(db=db, FM=FM(True))
    result = tr.translate("Hello", dest="fr", src="en")
    assert result == "Bonjour"

    hash_value = to_hash("Hello")
    hash_index = db.select_texts(hash_value)
    assert hash_index is not None

    check = db.select_translations(hash_index, "fr")
    assert check is not None