import time

from codegen import get_c_code_from_g4f
from runner import run_code_locally

ERROR_FALLBACK_CODE = """#include <stdio.h>
int main() {
    printf("Error processing this question.\\n");
    return 0;
}"""


def process_question(question, question_number, total_questions):
    print(f"Processing Question {question_number}/{total_questions}")
    start_time = time.time()

    try:
        code = get_c_code_from_g4f(question)
        output = run_code_locally(code)
        elapsed = time.time() - start_time
        print(f"Finished Question {question_number} in {elapsed:.2f} seconds")
        return question_number, question, code, output
    except Exception as err:
        print(f"Error processing question {question_number}: {err}")
        return question_number, question, ERROR_FALLBACK_CODE, f"Error: {err}"
