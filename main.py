import concurrent.futures
import time

from config import FINAL_PDF, MAX_WORKERS, QUESTIONS_FILE
from pdf_builder import create_pdf
from processor import process_question
from question_io import read_questions_from_file

def main():
    start_time = time.time()

    questions = read_questions_from_file(QUESTIONS_FILE)
    total_questions = len(questions)

    if not questions:
        print(f"No questions found in {QUESTIONS_FILE}. Please add questions and run again.")
        return

    print(f"Processing {total_questions} questions...")

    processed_questions = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(MAX_WORKERS, total_questions)) as executor:
        future_to_question = {
            executor.submit(process_question, q, i, total_questions): i
            for i, q in enumerate(questions, 1)
        }

        for future in concurrent.futures.as_completed(future_to_question):
            try:
                result = future.result()
                processed_questions.append(result)
            except Exception as err:
                print(f"Future failed: {err}")

    processed_questions.sort()
    create_pdf(processed_questions, FINAL_PDF)

    total_time = time.time() - start_time
    print(f"Total processing time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
