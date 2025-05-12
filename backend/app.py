import os
import json
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from backend.llm import llm_call, parse_llm_to_json
from backend.file_processor import extract_text_from_pdf, save_to_excel

ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UI'))
app = Flask(
    __name__,
    template_folder = ui_path)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

# Ensure the uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_cv_details(cv_text: str) -> str:
    return llm_call(text=cv_text)

def parse_llm_output(llm_output: str) -> json:
    return parse_llm_to_json(llm_output=llm_output)

def process_cv(pdf_path) -> None:
    """Extract text from PDF, call Groq to extract details, and save the results."""
    cv_text = extract_text_from_pdf(pdf_path)
    print("Extration is Done...")
    print(f"cv_text:{cv_text}")
    llm_output = extract_cv_details(cv_text)
    print("llm call is Done...")
    print(f"llm_output: {llm_output}")
    details = parse_llm_output(llm_output)
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
