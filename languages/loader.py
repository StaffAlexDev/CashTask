from config.buttons_config import LANGUAGE_REGISTRY
from languages.lang_base import LangBase


def get_lang(lang_code: str) -> LangBase:
    return LANGUAGE_REGISTRY.get(lang_code, LANGUAGE_REGISTRY["ru"])[1]
