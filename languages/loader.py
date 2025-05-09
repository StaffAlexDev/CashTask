from languages.lang_base import LangBase
from languages.ru import lang as ru_lang
from languages.en import lang as en_lang


def get_lang(lang_code: str) -> LangBase:
    if lang_code == "ru":
        return ru_lang
    if lang_code == "en":
        return en_lang
    return ru_lang
