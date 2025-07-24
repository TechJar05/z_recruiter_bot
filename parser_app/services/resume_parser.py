import fitz  # PyMuPDF

def extract_text_from_pdf(file) -> str:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join(page.get_text() for page in doc)
