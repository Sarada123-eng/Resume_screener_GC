import fitz
import os
import sys
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        full_text = full_text.strip()

        if not full_text:
            log(f'WARNING: No text extracted from "{pdf_path}" — may be scanned')
            return ""

        return full_text

    except Exception as e:
        log(f'ERROR extracting "{pdf_path}": {e}')
        return ""

def extract_text_from_job(job_path: str) -> str:
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            log(f'WARNING: Empty job description file "{job_path}"')
            return ""

        return text

    except Exception as e:
        log(f'ERROR reading job file "{job_path}": {e}')
        return ""