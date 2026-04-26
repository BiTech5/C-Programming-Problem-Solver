from fpdf import FPDF

from text_utils import clean_text, trim_line


class ProblemPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Programming Problem Solutions", 0, 1, "C")
        self.ln(5)

    def add_problem(self, question_number, question, code, output):
        question = clean_text(question)
        code = clean_text(code)
        output = clean_text(output)

        if self.get_y() > 260:
            self.add_page()

        self.set_font("Arial", "B", 14)
        self.cell(0, 10, f"Question {question_number}", 0, 1, "L")
        self.ln(2)

        self.set_font("Arial", "", 11)
        self.multi_cell(0, 5, question)
        self.ln(5)

        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "C Code Solution:", 0, 1, "L")
        self.set_font("Courier", "", 9)
        self._add_block_lines(code.split("\n"))
        self.ln(5)

        if self.get_y() > 250:
            self.add_page()

        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "Execution Output:", 0, 1, "L")
        self.set_font("Courier", "", 9)
        self._add_block_lines(output.split("\n"))

        self.ln(10)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def _add_block_lines(self, lines):
        for line in lines:
            if self.get_y() > 270:
                self.add_page()
                self.set_font("Courier", "", 9)
            self.cell(0, 5, trim_line(line), 0, 1)


def create_pdf(processed_questions, pdf_path):
    pdf = ProblemPDF()
    for question_num, question, code, output in processed_questions:
        pdf.add_problem(question_num, question, code, output)
    pdf.output(pdf_path)
    print(f"PDF created: {pdf_path}")
    return pdf_path
