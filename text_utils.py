def clean_text(text):
    if not isinstance(text, str):
        return text

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "--",
        "\u2026": "...",
        "\u00b4": "'",
        "\u00b0": " degrees",
        "\u00b5": "u",
        "\u00b7": "*",
        "\u00a9": "(c)",
        "\u00ae": "(R)",
        "\u2122": "TM",
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text.encode("latin-1", errors="replace").decode("latin-1")


def trim_line(line, max_len=100):
    if len(line) <= max_len:
        return line
    return f"{line[: max_len - 3]}..."
