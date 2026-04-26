def read_questions_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [q.strip() for q in file.readlines() if q.strip()]
    except FileNotFoundError:
        print(f"File {file_path} not found. Creating an empty file.")
        with open(file_path, "w", encoding="utf-8"):
            pass
        return []
