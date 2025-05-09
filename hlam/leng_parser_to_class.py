import json
from pathlib import Path

SCHEMA_FILE = Path("languages/schema.json")
OUTPUT_FILE = Path("languages/lang_classes.py")


class ClassGenerator:
    def __init__(self):
        self.classes = []

    def generate_class(self, name: str, keys: dict):
        class_lines = [f"@dataclass", f"class {name}:"]

        if not keys:
            class_lines.append("    pass")
            self.classes.append("\n".join(class_lines))
            return name

        for key, value in keys.items():
            field_name = key

            if isinstance(value, dict):
                nested_class_name = self.generate_nested_class_name(name, key)
                class_lines.append(f"    {field_name}: {nested_class_name}")
                self.generate_class(nested_class_name, value)
            else:
                class_lines.append(f"    {field_name}: str")

        self.classes.append("\n".join(class_lines))
        return name

    @staticmethod
    def generate_nested_class_name(parent: str, child: str) -> str:
        return f"{parent}_{child}".title().replace("_", "")

    def build(self, schema: dict):
        self.generate_class("Lang", schema)
        return self.classes


def main():
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        schema = json.load(f)

    generator = ClassGenerator()
    classes = generator.build(schema)

    output = """from dataclasses import dataclass\n\n"""
    output += "\n\n".join(classes)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✅ Сгенерировано и сохранено в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
