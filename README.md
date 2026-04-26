# C Programming Problem Solver

Python utility that reads programming questions, generates C solutions via G4F, compiles/runs them locally, and exports a PDF report.

## Features

- AI-based C code generation using `g4f`
- Local compilation/execution via `gcc`
- Automatic input simulation for common `scanf` formats
- Parallel question processing
- PDF export with question, code, and runtime output
- Fallback handling for model/compile/runtime errors

## Requirements

- Python 3.6+
- GCC available on `PATH`
- Python packages:
  - `fpdf`
  - `g4f`

## Installation

1. Clone this repository.
2. Install dependencies:

```bash
pip install fpdf g4f
```

3. Ensure `gcc` is installed and callable from terminal.

## Usage

1. Create `questions.txt` with one question per line.
2. Run:

```bash
python3 main.py
```

3. Output PDF is created as `code_solutions.pdf`.

## Configuration

Edit values in `config.py`:

- `QUESTIONS_FILE` (default: `questions.txt`)
- `FINAL_PDF` (default: `code_solutions.pdf`)
- `MAX_WORKERS` (default: `4`)

## Project Structure

- `main.py`: Entry point and orchestration
- `config.py`: Central configuration
- `question_io.py`: Read questions from file
- `codegen.py`: G4F prompt/call and code cleanup
- `runner.py`: GCC compile + execution simulation
- `processor.py`: Per-question processing pipeline
- `pdf_builder.py`: PDF layout and rendering
- `text_utils.py`: Text cleanup and formatting helpers

## Example Input

```text
Write a program to find the factorial of a number.
Create a program that checks if a number is prime.
```

## Notes

- Generated prompts include student identification lines in the produced C code.
- Compilation timeout is 10 seconds; execution timeout is 5 seconds.
- Text is normalized for PDF Latin-1 compatibility.
