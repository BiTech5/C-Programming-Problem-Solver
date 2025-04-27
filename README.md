# C Programming Problem Solver

A Python utility that automatically generates C code solutions for programming problems, compiles them, and creates a comprehensive PDF report.

## Overview

This tool takes a list of programming problems from a text file, uses AI to generate C code solutions, compiles and runs the code locally, and produces a professional PDF document containing all problems, solutions, and execution outputs.

## Features

- **AI-Powered Code Generation**: Utilizes the G4F client API to generate C code solutions
- **Local Compilation & Testing**: Automatically compiles and runs the generated code
- **Input Simulation**: Intelligently detects and simulates user input requirements
- **Parallel Processing**: Processes multiple problems simultaneously for efficiency
- **Comprehensive PDF Reports**: Creates well-formatted PDF documentation with all solutions
- **Error Handling**: Gracefully handles compilation errors and execution timeouts

## Requirements

- Python 3.6+
- GCC compiler (accessible via PATH)
- Required Python packages:
  - fpdf
  - g4f

## Installation

1. Clone this repository or download the script
2. Install required Python packages:
```
pip install fpdf g4f
```
3. Ensure GCC is installed and accessible from your command line

## Usage

1. Create a `questions.txt` file with one programming problem per line
2. Run the script:
   ```
   python3 main.py
   ```
3. A PDF file named `code_solutions.pdf` will be generated with all solutions

## Configuration

You can adjust the following parameters at the top of the script:

- `QUESTIONS_FILE`: Path to the file containing programming problems (default: 'questions.txt')
- `OUTPUT_FOLDER`: Directory for storing temporary outputs (default: 'output')
- `FINAL_PDF`: Name of the output PDF file (default: 'code_solutions.pdf')
- `MAX_WORKERS`: Maximum number of parallel processes (default: 4)

## How It Works

1. The script reads programming problems from the `questions.txt` file
2. For each problem, it:
- Sends the problem to an AI model via G4F API to generate C code
- Compiles the generated code using GCC
- Detects input requirements from scanf statements
- Generates appropriate random inputs when needed
- Captures the execution output
3. All problems, code solutions, and outputs are compiled into a PDF document
4. The PDF includes proper formatting with:
- Problem statements
- C code solutions with syntax formatting
- Execution outputs
- Input/output simulation details

## Example

Input file (`questions.txt`):
```Code
Write a program to find the factorial of a number.
Create a program that checks if a number is prime.
```

Output: A PDF file containing each problem, its C code solution, and execution output.

## Customization

- Student information can be modified in the `get_c_code_from_g4f` function
- PDF formatting can be adjusted in the `ProblemPDF` class
- Input generation can be customized in the `generate_random_input` function

## Troubleshooting

- If compilation fails, check that GCC is properly installed
- If the AI fails to generate code, try adjusting the prompt in `get_c_code_from_g4f`
- For timeout errors, increase the timeout values in the `run_code_locally` function

## Notes

- The program automatically adds student identification information (name, roll number, section)
- Unicode characters in code or output are cleaned and converted to ASCII equivalents
- The tool handles timeouts for both compilation (10 seconds) and execution (5 seconds)
