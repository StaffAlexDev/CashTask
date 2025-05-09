# import os
# from functools import lru_cache
# from json import load
#
# from config.constants import LANGUAGE_DIR
#
#
# class LangDict(dict):
#     def __getattr__(self, name):
#         value = self.get(name)
#         if isinstance(value, dict):
#             return LangDict(value)
#         if value is None:
#             return f"[{name}]"
#         return value
#
#     def __call__(self, **kwargs):
#         if isinstance(self, str):
#             return self.format(**kwargs)
#         return self
#
#     def __setattr__(self, name, value):
#         self[name] = value
#
#
# def convert_lang(data: dict) -> LangDict:
#     return LangDict({
#         key: convert_lang(value) if isinstance(value, dict) else value
#         for key, value in data.items()
#     })
#
#
# @lru_cache(maxsize=10)
# def get_lang_file(lang_code: str) -> LangDict:
#     """Загрузить языковой файл и вернуть как LangDict"""
#     path = os.path.join(LANGUAGE_DIR, f"{lang_code}.json")
#
#     try:
#         with open(path, encoding="utf-8") as f:
#             data = load(f)
#             return convert_lang(data)
#     except Exception as e:
#         print(f"Ошибка при загрузке языка '{lang_code}': {e}")
#         return LangDict({})
