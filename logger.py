import os
import sys
from datetime import datetime
from config import OUTPUT_DIR

LOG_FILE = os.path.join(OUTPUT_DIR, "pipeline.log")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] {level}: {message}"
    print(formatted)
    sys.stdout.flush()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def log_resume_detected(candidate_id: str):
    log(f'Resume "{candidate_id}.pdf" detected')

def log_resume_extracted(candidate_id: str):
    log(f'Resume "{candidate_id}" extracted successfully')

def log_resume_indexed(candidate_id: str):
    log(f'Resume "{candidate_id}" embedded and indexed')

def log_job_detected(job_id: str):
    log(f'Job description "{job_id}.txt" detected — will trigger re-ranking')

def log_ranking_updated(trigger: str):
    log(f'Ranking updated — trigger: {trigger}')

def log_feedback_received(feedback_id: str):
    log(f'Feedback "{feedback_id}" received — logged')

def log_warning(message: str):
    log(message, level="WARNING")

def log_error(message: str):
    log(message, level="ERROR")