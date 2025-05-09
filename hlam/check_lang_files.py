import json
from pathlib import Path


def load_json(file_path):
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_schema(schema, data, path=""):
    """
    Рекурсивно добавляет отсутствующие ключи из схемы в данные.
    Возвращает True если были изменения.
    """
    updated = False

    for key, value in schema.items():
        full_path = f"{path}.{key}" if path else key

        if key not in data:
            print(f"➕ Добавлен недостающий ключ: {full_path}")
            data[key] = "" if not isinstance(value, dict) else {}
            updated = True

        if isinstance(value, dict):
            if not isinstance(data[key], dict):
                print(f"⚠️ Конфликт типов (заменено на dict): {full_path}")
                data[key] = {}
                updated = True

            # Рекурсивно проверяем вложенные
            if merge_schema(value, data[key], full_path):
                updated = True

    return updated


def check_and_update_language(schema_file: Path, lang_file: Path):
    schema = load_json(schema_file)
    lang = load_json(lang_file)

    print(f"\n🔍 Проверка {lang_file.name}")

    if merge_schema(schema, lang):
        save_json(lang_file, lang)
        print(f"✅ Файл {lang_file.name} обновлён.")
    else:
        print(f"✅ Файл {lang_file.name} уже полный. Нет недостающих ключей.")


if __name__ == "__main__":
    schema_path = Path("language/schema.json")

    # Список языков
    lang_files = [
        Path("language/ru.json"),
        Path("language/en.json"),
        # Добавляйте другие языки сюда
    ]

    if not schema_path.exists():
        print("❌ Не найден schema.json!")
        exit(1)

    for lang_file in lang_files:
        check_and_update_language(schema_path, lang_file)
