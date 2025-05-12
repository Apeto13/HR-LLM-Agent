import pandas as pd
from PyPDF2 import PdfReader
import re

def extract_text_from_pdf(pdf_path) -> str:
    """Extract text from all pages of the PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def save_to_excel(extracted_data, excel_file="candidates.xlsx") -> None:
    """Append the extracted data as a new row into an Excel file."""
    try:
        df = pd.read_excel(excel_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Candidate Name", "Years of Experience", "Last Job Title",
            "Highest Education", "Certificates", "Employment Gaps"
        ])
    new_row = pd.DataFrame([{
        "Candidate Name": extracted_data.get("name"),
        "Years of Experience": extracted_data.get("experience"),
        "Last Job Title": extracted_data.get("last_job"),
        "Highest Education": extracted_data.get("education"),
        "Certificates": extracted_data.get("certificates"),
        "Employment Gaps": extracted_data.get("gaps")
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(excel_file, index=False)
