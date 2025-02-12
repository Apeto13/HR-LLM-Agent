import os
import json
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from PyPDF2 import PdfReader
from groq import Groq

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

# Ensure the uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# API key
API_KEY = "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"

# Initialize the Groq client (ensure you have set your API key in your environment)
client = Groq(api_key=API_KEY)

def extract_text_from_pdf(pdf_path):
    """Extract text from all pages of the PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_cv_details(cv_text):
    """
    Prepare a prompt and call Groq's API to extract candidate details.
    The prompt instructs the LLM to return a JSON with keys:
    name, experience, last_job, education, certificates, gaps.
    """
    prompt = f"""
    Extract the following details from the CV:
    - Candidate Name
    - Total Years of Experience
    - Last Job Title
    - Highest Education Level
    - Any Professional Certificates
    - Any Gaps in Employment

    CV Text:
    {cv_text}

    Please return the result as JSON with keys: name, experience, last_job, education, certificates, gaps.
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="deepseek-r1-distill-llama-70b",  # choose the appropriate model for your use case
        temperature=0.0
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def parse_llm_output(llm_output):
    """Attempt to parse the LLM output as JSON. Return a dictionary."""
    try:
        data = json.loads(llm_output)
    except json.JSONDecodeError:
        data = {}
    return data

def save_to_excel(extracted_data, excel_file="candidates.xlsx"):
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

def process_cv(pdf_path):
    """Extract text from PDF, call Groq to extract details, and save the results."""
    cv_text = extract_text_from_pdf(pdf_path)
    llm_output = extract_cv_details(cv_text)
    details = parse_llm_output(llm_output)
    save_to_excel(details)

@app.route("/download_excel")
def download_excel():
    # Ensure the Excel file exists
    excel_path = "candidates.xlsx"
    if os.path.exists(excel_path):
        # Return the file as an attachment (the file will be downloaded)
        return send_file(excel_path, as_attachment=True, download_name="candidates.xlsx")
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

if __name__ == '__main__':
    app.run(debug=True)
