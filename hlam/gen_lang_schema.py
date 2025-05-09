import json
import sys
from pathlib import Path


def generate_schema(data):
    """Рекурсивно обходит словарь и заменяет все значения на пустые строки"""
    if isinstance(data, dict):
        return {key: generate_schema(value) for key, value in data.items()}
    return ""


def create_schema(source_file: Path, output_file: Path):
    with open(source_file, "r", encoding="utf-8") as f:
        lang_data = json.load(f)

    schema = generate_schema(lang_data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    print(f"✅ Схема создана: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python gen_lang_schema.py ru.json schema.json")
        sys.exit(1)

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])

    if not source.exists():
        print(f"❌ Файл не найден: {source}")
        sys.exit(1)

    create_schema(source, output)
