import logging
from cython_code.my_translator import MyTranslator


def translator(text, dest, file_path='db/translate.json', real=False):
    try:
        if dest == 'en' or not dest or not text:
            return text
        else:
            data = MyTranslator(file_path=file_path,
                                text=text,
                                lang=dest,
                                real=real)
        result = data.translator()
        return result
    except Exception as err:
        logging.error(err)
        return text
