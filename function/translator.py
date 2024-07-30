import json
import logging
from deep_translator import GoogleTranslator
from data.config import yil_oy_kun, soat_minut_sekund


def translator(text, dest, file_path='data/translate.json', real=False):
    """
    Translates the given text to the specified language using a translation cache or an online translator.

    Parameters:
    - text: The text to translate.
    - dest: The target language code (e.g., 'en' for English, 'es' for Spanish).
    - file_path: The path to the JSON file used to store cached translations (default: 'data/translate.json').
    - real: A boolean indicating whether to use the online translation service (True) or the cached translation (False).

    Returns:
    - The translated text if successful, or the original text if an error occurs or no translation is needed.
    """
    try:
        # If no translation is needed, return the original text
        if dest == 'en' or not dest or not text:
            return text
        else:
            # Use the MyTranslator class to handle translation and caching
            data = MyTranslator(file_path=file_path, text=text, lang=dest, real=real)
        result = data.translator()
        return result
    except Exception as err:
        logging.error(err)
        return text


class MyTranslator:
    def __init__(self, file_path, text, lang, real=False):
        """
        Initializes the MyTranslator object.

        Parameters:
        - file_path: Path to the JSON file containing cached translations.
        - text: The text to translate.
        - lang: The target language code.
        - real: Boolean to determine if real-time translation should be used.
        """
        self.file_path = file_path
        self.text = text
        self.lang = lang
        self.real = real

        try:
            # Load cached translations from JSON file
            with open(self.file_path, "r") as json_file:
                self.json_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file not found or corrupted, create a new JSON file
            data = {"date": str(yil_oy_kun) + ' / ' + str(soat_minut_sekund)}
            with open(self.file_path, "w") as json_file:
                json.dump(data, json_file)
            with open(self.file_path, "r") as json_file:
                self.json_data = json.load(json_file)

    def translator(self):
        """
        Translates the text using either cached data or an online translation service.

        Returns:
        - Translated text if successful, otherwise the original text.
        """
        try:
            if self.real:
                # Use GoogleTranslator for real-time translation
                return GoogleTranslator(source='auto', target=self.lang).translate(self.text)

            try:
                # Try to get the translation from the cache
                return self.json_data[self.text][self.lang]
            except:
                # If translation is not found in the cache, use GoogleTranslator
                result = GoogleTranslator(source='auto', target=self.lang).translate(self.text)
                data = {self.lang: result}
                try:
                    # Cache the new translation
                    self.json_data[self.text] = data
                    with open(self.file_path, "w") as json_file:
                        json.dump(self.json_data, json_file)
                except Exception as err:
                    logging.error(err)
                return result
        except Exception as err:
            logging.error(err)
            return self.text
