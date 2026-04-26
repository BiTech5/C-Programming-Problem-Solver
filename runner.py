import os
import random
import re
import subprocess
import tempfile

from text_utils import clean_text


def generate_random_input(match_type):
    if match_type == "d":
        return str(random.randint(1, 100))
    if match_type == "f":
        return f"{random.uniform(1, 100):.2f}"
    if match_type == "c":
        return random.choice("abcdefghijklmnopqrstuvwxyz")
    if match_type == "s":
        return random.choice(["apple", "banana", "cherry", "date", "elderberry"])
    return "42"


def run_code_locally(code):
    with tempfile.TemporaryDirectory() as tmpdirname:
        c_file = os.path.join(tmpdirname, "program.c")
        exe_file = os.path.join(tmpdirname, "program.out")

        with open(c_file, "w", encoding="utf-8") as file:
            file.write(code)

        try:
            compile_result = subprocess.run(
                ["gcc", "-O2", c_file, "-o", exe_file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if compile_result.returncode != 0:
                return clean_text(f"Compilation failed:\n{compile_result.stderr}")

            # Supports optional width/precision and length modifiers before d/f/c/s.
            format_specifiers = re.findall(r"%[-+0-9.*]*(?:hh|h|l|ll|L)?([dfcs])", code)
            if not format_specifiers:
                return _run_without_input(exe_file)

            return _run_with_generated_input(code, exe_file, format_specifiers)
        except Exception as err:
            return clean_text(f"Error: {err}")


def _run_without_input(exe_file):
    try:
        result = subprocess.run([exe_file], capture_output=True, text=True, timeout=5)
        return clean_text(result.stdout + result.stderr)
    except subprocess.TimeoutExpired:
        return "Program execution timed out (5 seconds)"


def _run_with_generated_input(code, exe_file, format_specifiers):
    inputs = [generate_random_input(fmt) for fmt in format_specifiers]

    prompt_pattern = r'printf\s*\(\s*["\']([^"\']*)["\']'
    potential_prompts = re.findall(prompt_pattern, code)

    formatted_inputs = []
    for index, input_val in enumerate(inputs):
        if index < len(potential_prompts):
            prompt = potential_prompts[index].replace("\\n", "").strip()
            formatted_inputs.append(f"{prompt}{input_val}")
        else:
            formatted_inputs.append(input_val)

    input_string = "\n".join(inputs)
    display_inputs = "\n".join(formatted_inputs)

    try:
        result = subprocess.run(
            [exe_file], input=input_string, capture_output=True, text=True, timeout=5
        )
        return clean_text(
            "Input/Output Simulation:\n"
            f"{display_inputs}\n\nProgram Output:\n{result.stdout}{result.stderr}"
        )
    except subprocess.TimeoutExpired:
        return clean_text(
            "Input/Output Simulation:\n"
            f"{display_inputs}\n\nProgram execution timed out (5 seconds)"
        )
