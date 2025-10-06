import fitz

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """ 
    Extracts text content from a PDF file provided as bytes.
    """
    try:
        # Open the PDF from bytes
        pdf_documents = fitz.open(stream=pdf_bytes, filetype="pdf")

        full_text = []
        for page_num in range(len(pdf_documents)):
            page = pdf_documents.load_page(page_num)
            full_text.append(page.get_text())

        return "\n".join(full_text)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
