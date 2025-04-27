import os
import time
import subprocess
import tempfile
import concurrent.futures
import re
import random
from functools import lru_cache
from fpdf import FPDF
from g4f.client import Client

# Configuration
QUESTIONS_FILE = 'questions.txt'
OUTPUT_FOLDER = 'output'
FINAL_PDF = 'code_solutions.pdf'
MAX_WORKERS = 4  # Adjust based on your system's capabilities

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def clean_text(text):
    """Replace problematic Unicode chars with ASCII equivalents."""
    replacements = {
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\u2026': '...', # Ellipsis
        '\u00b4': "'",  # Acute accent
        '\u00b0': " degrees", # Degree sign
        '\u00b5': "u",  # Micro sign
        '\u00b7': "*",  # Middle dot
        '\u00a9': "(c)", # Copyright sign
        '\u00ae': "(R)", # Registered trademark
        '\u2122': "TM",  # Trademark
    }
    
    if not isinstance(text, str):
        return text
        
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Replace any other non-Latin1 characters with '?'
    return text.encode('latin-1', errors='replace').decode('latin-1')

def read_questions_from_file(file_path):
    """Read questions from file, caching results."""
    try:
        with open(file_path, 'r') as file:
            return [q.strip() for q in file.readlines() if q.strip()]
    except FileNotFoundError:
        print(f"File {file_path} not found. Creating an empty file.")
        with open(file_path, 'w') as file:
            pass
        return []

@lru_cache(maxsize=128)
def get_c_code_from_g4f(question):
    """Get C code solution using g4f client API."""
    prompt = (
        f"Write C code to solve the following problem and don't use function and "
        f"add last add printf('Name: Ashmita Khatri') printf('Roll n.o:274') printf('Section E'). "
        f"Only provide the code, no explanations:\n\n{question}"
    )
    
    try:
        # Create client
        client = Client()
        
        # First try with gpt-4o-mini
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a C programming expert. Provide only code, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                web_search=False,
                timeout=20
            )
            code = response.choices[0].message.content.strip()
            
            # If we got a valid response, process it
            if code and len(code) > 20:  # Basic validation
                if code.startswith('```'):
                    code_parts = code.split('```')
                    if len(code_parts) > 1:
                        code = code_parts[1].strip()
                        if code.startswith('c') or code.startswith('C'):
                            code = code[1:].strip()
                return clean_code(code)
        except Exception as e:
            print(f"gpt-4o-mini failed: {str(e)}")
            
        # Fallback to gpt-3.5-turbo
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a C programming expert. Provide only code, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                web_search=False,
                timeout=20
            )
            code = response.choices[0].message.content.strip()
            
            # If we got a valid response, process it
            if code and len(code) > 20:  # Basic validation
                if code.startswith('```'):
                    code_parts = code.split('```')
                    if len(code_parts) > 1:
                        code = code_parts[1].strip()
                        if code.startswith('c') or code.startswith('C'):
                            code = code[1:].strip()
                return clean_code(code)
        except Exception as e:
            print(f"gpt-3.5-turbo failed: {str(e)}")
    
    except Exception as main_e:
        print(f"G4F client error: {str(main_e)}")
    
    # Fallback code if all attempts fail
    return """#include <stdio.h>

int main() {
    printf("Failed to generate code for the question.\\n");
    printf("Name: Ashmita Khatri\\n");
    printf("Roll n.o:274\\n");
    printf("Section E\\n");
    return 0;
}
"""

def clean_code(code):
    """Clean up code by fixing escape characters and removing explanations."""
    # Clean any unicode characters
    code = clean_text(code)
    
    # Remove any text before #include or after the final }
    code_start = code.find("#include")
    if code_start != -1:
        code = code[code_start:]
    
    # Make sure the code ends properly
    last_brace = code.rfind("}")
    if last_brace != -1:
        code = code[:last_brace+1]
    
    # Fix potential escape character issues
    code = code.replace("\\n", "\\n")
    
    return code

def generate_random_input(match_type):
    """Generate appropriate random input based on format specifier."""
    if match_type == 'd':
        return str(random.randint(1, 100))
    elif match_type == 'f':
        return f"{random.uniform(1, 100):.2f}"
    elif match_type == 'c':
        return random.choice('abcdefghijklmnopqrstuvwxyz')
    elif match_type == 's':
        words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
        return random.choice(words)
    else:
        return '42'

def run_code_locally(code):
    """Compile and run C code with better input handling."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        c_file = os.path.join(tmpdirname, "program.c")
        exe_file = os.path.join(tmpdirname, "program.out")
        
        with open(c_file, "w") as f:
            f.write(code)
        
        try:
            # Compile with optimizations
            compile_result = subprocess.run(
                ["gcc", "-O2", c_file, "-o", exe_file], 
                capture_output=True, 
                text=True,
                timeout=10
            )

            if compile_result.returncode != 0:
                return clean_text(f"Compilation failed:\n{compile_result.stderr}")

            # Find all scanf format specifiers for input simulation
            format_specifiers = re.findall(r'%([dfcs])', code)
            
            if not format_specifiers:
                # No input needed, just run the program
                try:
                    result = subprocess.run(
                        [exe_file], 
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    return clean_text(result.stdout + result.stderr)
                except subprocess.TimeoutExpired:
                    return "Program execution timed out (5 seconds)"
            else:
                # Generate inputs based on format specifiers
                inputs = [generate_random_input(fmt) for fmt in format_specifiers]
                
                # Extract input prompts from code (typical printf before scanf)
                # Look for printf statements that likely contain prompts
                prompt_pattern = r'printf\s*\(\s*["\']([^"\']*)["\']'
                potential_prompts = re.findall(prompt_pattern, code)
                
                # Format the input display with prompts when available
                formatted_inputs = []
                for i, input_val in enumerate(inputs):
                    # Try to find a matching prompt for this input
                    if i < len(potential_prompts):
                        prompt = potential_prompts[i]
                        # Clean the prompt (remove escape chars)
                        prompt = prompt.replace('\\n', '').strip()
                        formatted_inputs.append(f"{prompt}{input_val}")
                    else:
                        formatted_inputs.append(input_val)
                
                # Join inputs for subprocess
                input_string = '\n'.join(inputs)
                
                # Create a nicely formatted display version
                display_inputs = '\n'.join(formatted_inputs)
                
                try:
                    result = subprocess.run(
                        [exe_file], 
                        input=input_string,
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    return clean_text(f"Input/Output Simulation:\n{display_inputs}\n\nProgram Output:\n{result.stdout}{result.stderr}")
                except subprocess.TimeoutExpired:
                    return clean_text(f"Input/Output Simulation:\n{display_inputs}\n\nProgram execution timed out (5 seconds)")

        except Exception as e:
            return clean_text(f"Error: {str(e)}")

class ProblemPDF(FPDF):
    """Custom PDF class with header and footer."""
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Programming Problem Solutions", 0, 1, "C")
        self.ln(5)

    def add_problem(self, question_number, question, code, output):
        """Add a complete problem with question, code and output to the PDF."""
        # Clean all text inputs to ensure they're latin-1 compatible
        question = clean_text(question)
        code = clean_text(code)
        output = clean_text(output)
        
        # Check if we need a new page
        if self.get_y() > 260:  # Near bottom of page
            self.add_page()
        
        # Start with question number and title
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, f"Question {question_number}", 0, 1, "L")
        self.ln(2)
        
        # Question text
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 5, question)
        self.ln(5)
        
        # Code section
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "C Code Solution:", 0, 1, "L")
        self.set_font("Courier", "", 9)  # Monospaced font for code
        
        # Format and add code
        code_lines = code.split('\n')
        for line in code_lines:
            # Check if we need a page break
            if self.get_y() > 270:  # Near bottom of page
                self.add_page()
                self.set_font("Courier", "", 9)
            
            # Trim very long lines
            if len(line) > 100:
                line = line[:97] + "..."
            self.cell(0, 5, line, 0, 1)
        self.ln(5)
        
        # Check if we need a page break before output
        if self.get_y() > 250:
            self.add_page()
        
        # Output section
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "Execution Output:", 0, 1, "L")
        self.set_font("Courier", "", 9)
        
        # Format and add output
        output_lines = output.split('\n')
        for line in output_lines:
            # Check if we need a page break
            if self.get_y() > 270:
                self.add_page()
                self.set_font("Courier", "", 9)
            
            # Trim very long lines
            if len(line) > 100:
                line = line[:97] + "..."
            self.cell(0, 5, line, 0, 1)
        
        # Add separator line
        self.ln(10)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

def process_question(question, question_number, total_questions):
    """Process a single question."""
    print(f"Processing Question {question_number}/{total_questions}")
    start_time = time.time()
    
    try:
        # Get code
        code = get_c_code_from_g4f(question)
        
        # Run code and capture output
        output = run_code_locally(code)
        
        elapsed = time.time() - start_time
        print(f"Finished Question {question_number} in {elapsed:.2f} seconds")
        
        return (question_number, question, code, output)
    except Exception as e:
        print(f"Error processing question {question_number}: {str(e)}")
        # Return fallback data
        return (question_number, question, 
                "#include <stdio.h>\nint main() {\n    printf(\"Error processing this question.\\n\");\n    return 0;\n}", 
                f"Error: {str(e)}")

def create_pdf(processed_questions):
    """Create a PDF with all questions, code, and output."""
    pdf = ProblemPDF()
    
    for question_num, question, code, output in processed_questions:
        pdf.add_problem(question_num, question, code, output)
    
    pdf_path = FINAL_PDF
    pdf.output(pdf_path)
    print(f"PDF created: {pdf_path}")
    return pdf_path

def main():
    start_time = time.time()
    
    # Read questions
    questions = read_questions_from_file(QUESTIONS_FILE)
    total_questions = len(questions)
    
    if not questions:
        print(f"No questions found in {QUESTIONS_FILE}. Please add questions and run again.")
        return
    
    print(f"Processing {total_questions} questions...")
    
    # Process questions in parallel
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
            except Exception as e:
                print(f"Future failed: {str(e)}")
    
    # Sort by question number
    processed_questions.sort()
    
    # Create PDF with all results
    create_pdf(processed_questions)
    
    total_time = time.time() - start_time
    print(f"Total processing time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()