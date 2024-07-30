import json
import logging

from deep_translator import GoogleTranslator

from data.config import yil_oy_kun, soat_minut_sekund


def translator(text, dest, file_path='data/translate.json', real=False):
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


class MyTranslator:
    def __init__(self, file_path, text, lang, real=False):
        self.file_path = file_path
        self.text = text
        self.lang = lang
        self.real = real
        try:
            with open(self.file_path, "r") as json_file:
                self.json_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"date": str(yil_oy_kun) + ' / ' + str(soat_minut_sekund)}
            with open(self.file_path, "w") as json_file:
                json.dump(data, json_file)
            with open(self.file_path, "r") as json_file:
                self.json_data = json.load(json_file)

    def translator(self, ):
        try:
            if self.real:
                return GoogleTranslator(source='auto', target=self.lang).translate(self.text)
            try:
                return self.json_data[self.text][self.lang]
            except:
                pass
                result = GoogleTranslator(source='auto', target=self.lang).translate(self.text)
                data = {
                    self.lang: result
                }
                try:
                    self.json_data[self.text] = data
                    with open(self.file_path, "w") as json_file:
                        json.dump(self.json_data, json_file)
                except Exception as err:
                    logging.error(err)
                return result
        except Exception as err:
            logging.error(err)
            return self.text