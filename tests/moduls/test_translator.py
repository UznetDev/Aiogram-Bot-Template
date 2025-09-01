from bot.loader import translator, FM



async def test_translator_no_feature():

    feature = FM.feature('translator')

    FM.upsert_feature('translator', False)

    result = translator("Hello", dest="fr", src="en")
    assert result == "Hello"

    FM.upsert_feature('translator', True)
    assert FM.feature('translator') == True

    result = translator.translate("Hello", dest="fr", src="en")
    assert result == "Bonjour"

    FM.upsert_feature('translator', feature)
