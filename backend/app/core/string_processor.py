import csv
from pathlib import Path

import wordninja


def _open_synonym_dict() -> dict[str, str]:
    with open(Path(__file__).parent.parent / 'data' / 'synonym_list.csv', 'r', encoding='utf-8') as f:
        return {slang: synonym for slang, synonym in csv.reader(f, delimiter=',')}

class StringProcessor:

    _synonym_dict: dict[str, str] = _open_synonym_dict()

    @staticmethod
    def add_spaces(string: str) -> str:
        """
        Добавить пробелы в строку.

        :param string: Исходная строка

        :return: Преобразованная строка
        """
        # Загрузка словаря русских слов
        wordninja.language_model_path = 'wordninja_ru_words.txt.gz'

        words = wordninja.split(string)
        return ' '.join(words)

    @classmethod
    def slang_translate(cls, string: str) -> str:
        word_list = string.replace( '\n', ' ').split()
        for _ in range(len(word_list)):
            if word_list[_] in cls._synonym_dict:
                word_list[_] = cls._synonym_dict[word_list[_]]
        return ' '.join(word_list)

    @classmethod
    def refactor_string(cls, string: str) -> str:
        string_lower = string.lower()

        # Processing string
        processed_string = cls.slang_translate(string_lower)

        return processed_string
