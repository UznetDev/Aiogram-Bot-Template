import json
import logging
from deep_translator import GoogleTranslator
from data.config import yil_oy_kun, soat_minut_sekund

cdef class MyTranslator:
    cdef str file_path
    cdef str text
    cdef str lang
    cdef bint real
    cdef dict json_data

    def __init__(self, str file_path, str text, str lang, bint real=False):
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

    def translator(self):
        try:
            if self.real:
                return GoogleTranslator(source='auto', target=self.lang).translate(self.text)
            try:
                return self.json_data[self.text][self.lang]
            except KeyError:
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