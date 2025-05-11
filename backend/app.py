import os
import json
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from PyPDF2 import PdfReader
from groq import Groq
from backend.llm import llm_call, parse_llm_to_json
from backend.file_processor import extract_text_from_pdf, save_to_excel, cleaning_llm

ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UI'))
app = Flask(
    __name__,
    template_folder = ui_path)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

# Ensure the uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# def extract_text_from_pdf(pdf_path) -> str:
#     """Extract text from all pages of the PDF file."""
#     reader = PdfReader(pdf_path)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() + "\n"
#     return text

# def extract_cv_details(cv_text):
#     """
#     Prepare a prompt and call Groq's API to extract candidate details.
#     The prompt instructs the LLM to return a JSON with keys:
#     name, experience, last_job, education, certificates, gaps.
#     """
#     prompt = f"""
#     Extract the following details from the CV:
#     - Candidate Name
#     - Total Years of Experience
#     - Last Job Title
#     - Highest Education Level
#     - Any Professional Certificates
#     - Any Gaps in Employment

#     CV Text:
#     {cv_text}

#     Please return the result as JSON with keys: name, experience, last_job, education, certificates, gaps.
#     """
#     response = client.chat.completions.create(
#         messages=[{"role": "user", "content": prompt}],
#         model="deepseek-r1-distill-llama-70b",  # choose the appropriate model for your use case
#         temperature=0.0
#     )
#     print(response.choices[0].message.content)
#     return response.choices[0].message.content

def extract_cv_details(cv_text: str) -> str:
    return llm_call(text=cv_text)

# def parse_llm_output(llm_output):
#     """Attempt to parse the LLM output as JSON. Return a dictionary."""
#     try:
#         data = json.loads(llm_output)
#     except json.JSONDecodeError:
#         data = {}
#     return data

def parse_llm_output(llm_output: str) -> json:
    return parse_llm_to_json(llm_output=llm_output)

# def save_to_excel(extracted_data, excel_file="candidates.xlsx"):
#     """Append the extracted data as a new row into an Excel file."""
#     try:
#         df = pd.read_excel(excel_file)
#     except FileNotFoundError:
#         df = pd.DataFrame(columns=[
#             "Candidate Name", "Years of Experience", "Last Job Title",
#             "Highest Education", "Certificates", "Employment Gaps"
#         ])
#     new_row = pd.DataFrame([{
#         "Candidate Name": extracted_data.get("name"),
#         "Years of Experience": extracted_data.get("experience"),
#         "Last Job Title": extracted_data.get("last_job"),
#         "Highest Education": extracted_data.get("education"),
#         "Certificates": extracted_data.get("certificates"),
#         "Employment Gaps": extracted_data.get("gaps")
#     }])
#     df = pd.concat([df, new_row], ignore_index=True)
#     df.to_excel(excel_file, index=False)

def process_cv(pdf_path) -> None:
    """Extract text from PDF, call Groq to extract details, and save the results."""
    cv_text = extract_text_from_pdf(pdf_path)
    print("Extration is Done...")
    print(f"cv_text:{cv_text}")
    llm_output = extract_cv_details(cv_text)
    print("llm call is Done...")
    print(f"llm_output: {llm_output}")
    cleaned = cleaning_llm(llm_output)
    print(f"cleaned: {cleaned}")
    details = parse_llm_output(cleaned)
    print(f"parsing :{details}")
    print("parsing is Done...")
    save_to_excel(details)
    print("Excel file is Saved! ")

@app.route("/download_excel")
def download_excel():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    excel_path = os.path.join(root_dir, "candidates.xlsx")
    if os.path.exists(excel_path):
        return send_file(
            excel_path,
            as_attachment=True,
            download_name="candidates.xlsx"
        )
    else:
        flash("Excel file not found. Process a CV first.")
        return redirect(url_for("upload_cv"))

@app.route("/", methods=["GET", "POST"])
def upload_cv():
    if request.method == "POST":
        if "cv_file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["cv_file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and file.filename.lower().endswith(".pdf"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            process_cv(filepath)
            flash("CV processed and data added to Excel!")
            return redirect(url_for("upload_cv"))
    return render_template("upload.html")

# if __name__ == '__main__':
#     app.run(debug=True)
