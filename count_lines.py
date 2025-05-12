import os

IGNORED_DIRS = {".idea", "__pycache__", ".git", "venv", ".dokadancevenv"}
IGNORED_FILES = {".env"}
VENV_PREFIX = ".venv"


def is_code_line(line: str) -> bool:
    """Определяет, является ли строка полезной (не пустой и не комментарием)"""
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("#")


def count_code_lines_in_file(filepath):
    code_lines = 0
    total_lines = 0

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total_lines += 1
            if is_code_line(line):
                code_lines += 1

    return total_lines, code_lines


def count_code_lines_in_project(directory, extensions=(".py",)):
    total_lines = 0
    total_code_lines = 0
    files_counted = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs
            if d not in IGNORED_DIRS and not d.startswith(VENV_PREFIX)
        ]

        for file in files:
            if file in IGNORED_FILES:
                continue

            if file.endswith(extensions):
                filepath = os.path.join(root, file)
                file_total, file_code = count_code_lines_in_file(filepath)
                total_lines += file_total
                total_code_lines += file_code
                files_counted += 1
                print(f"{filepath}: {file_total} lines, {file_code} code lines")

    print("\n==========")
    print(f"Total files: {files_counted}")
    print(f"Total lines (including empty and comments): {total_lines}")
    print(f"Total code lines (excluding empty and comments): {total_code_lines}")

    return total_code_lines


def print_project_structure(directory, prefix=""):
    """Выводит дерево файлов проекта"""
    entries = os.listdir(directory)
    entries = [
        e for e in entries
        if e not in IGNORED_DIRS and e not in IGNORED_FILES and not e.startswith(VENV_PREFIX)]
    entries.sort()

    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "

        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if index == len(entries) - 1 else "│   "
            print_project_structure(path, prefix + extension)


if __name__ == "__main__":
    project_dir = os.path.dirname(__file__)

    # print("=== Project Structure ===")
    # print_project_structure(project_dir)

    print("\n=== Code Lines Stats ===")
    count_code_lines_in_project(project_dir)
