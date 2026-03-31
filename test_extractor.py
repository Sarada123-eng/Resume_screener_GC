from extractor import extract_text_from_pdf, extract_text_from_job
import os

print("=== Testing PDF extraction ===\n")

resume_files = os.listdir("data/resumes")
for filename in resume_files[:3]:
    path = os.path.join("data/resumes", filename)
    text = extract_text_from_pdf(path)
    print(f"File: {filename}")
    print(f"Characters extracted: {len(text)}")
    print(f"Preview: {text[:100].strip()}")
    print("-" * 40)

print("\n=== Testing JD extraction ===\n")

job_files = os.listdir("data/jobs")
for filename in job_files:
    path = os.path.join("data/jobs", filename)
    text = extract_text_from_job(path)
    print(f"File: {filename}")
    print(f"Characters extracted: {len(text)}")
    print(f"Preview: {text[:100].strip()}")
    print("-" * 40)