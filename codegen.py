from functools import lru_cache

from g4f.client import Client

from text_utils import clean_text

FALLBACK_CODE = """#include <stdio.h>

int main() {
    printf("Failed to generate code for the question.\\n");
    printf("Name: Ashmita Khatri\\n");
    printf("Roll n.o:274\\n");
    printf("Section E\\n");
    return 0;
}
"""


def clean_code(code):
    code = clean_text(code)

    code_start = code.find("#include")
    if code_start != -1:
        code = code[code_start:]

    last_brace = code.rfind("}")
    if last_brace != -1:
        code = code[: last_brace + 1]

    return code


def _extract_code_block(content):
    code = content.strip()
    if code.startswith("```"):
        code_parts = code.split("```")
        if len(code_parts) > 1:
            code = code_parts[1].strip()
            if code.startswith("c") or code.startswith("C"):
                code = code[1:].strip()
    return code


def _request_code(client, model, prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a C programming expert. Provide only code, no explanations.",
            },
            {"role": "user", "content": prompt},
        ],
        web_search=False,
        timeout=20,
    )
    return _extract_code_block(response.choices[0].message.content)


@lru_cache(maxsize=128)
def get_c_code_from_g4f(question):
    prompt = (
        "Write C code to solve the following problem and don't use function and "
        "add last add printf('Name: Ashmita Khatri') printf('Roll n.o:274') "
        "printf('Section E'). Only provide the code, no explanations:\n\n"
        f"{question}"
    )

    try:
        client = Client()
        for model in ("gpt-4o-mini", "gpt-3.5-turbo"):
            try:
                code = _request_code(client, model, prompt)
                if code and len(code) > 20:
                    return clean_code(code)
            except Exception as err:
                print(f"{model} failed: {err}")
    except Exception as err:
        print(f"G4F client error: {err}")

    return FALLBACK_CODE
