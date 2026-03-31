import pathway as pw
import time
import os
import sys
from datetime import datetime
from config import (
    RESUMES_DIR, JOBS_DIR, FEEDBACK_DIR,
    OUTPUT_DIR, DEBOUNCE_DELAY
)

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def get_candidate_id(filepath) -> str:
    filepath = str(filepath).strip('"')
    filename = os.path.basename(filepath)
    candidate_id = os.path.splitext(filename)[0]
    return candidate_id

def process_resume_path(path) -> str:
    time.sleep(DEBOUNCE_DELAY)
    candidate_id = get_candidate_id(path)
    log(f'Resume "{candidate_id}.pdf" detected')
    return candidate_id

def process_job_path(path) -> str:
    time.sleep(DEBOUNCE_DELAY)
    job_id = get_candidate_id(path)
    log(f'Job description "{job_id}.txt" detected — will trigger re-ranking')
    return job_id

def process_feedback_path(path) -> str:
    time.sleep(DEBOUNCE_DELAY)
    feedback_id = get_candidate_id(path)
    log(f'Feedback "{feedback_id}" received — logged')
    return feedback_id

os.makedirs(OUTPUT_DIR, exist_ok=True)

log("Starting Pathway pipeline...")
log(f"Watching: {RESUMES_DIR}")
log(f"Watching: {JOBS_DIR}")
log(f"Watching: {FEEDBACK_DIR}")

resumes_raw = pw.io.fs.read(
    RESUMES_DIR,
    format="binary",
    mode="streaming",
    with_metadata=True
)

jobs_raw = pw.io.fs.read(
    JOBS_DIR,
    format="plaintext",
    mode="streaming",
    with_metadata=True
)

feedback_raw = pw.io.fs.read(
    FEEDBACK_DIR,
    format="plaintext",
    mode="streaming",
    with_metadata=True
)

resumes_detected = resumes_raw.select(
    candidate_id=pw.apply(
        process_resume_path,
        pw.this._metadata["path"]
    )
)

jobs_detected = jobs_raw.select(
    job_id=pw.apply(
        process_job_path,
        pw.this._metadata["path"]
    )
)

feedback_detected = feedback_raw.select(
    feedback_id=pw.apply(
        process_feedback_path,
        pw.this._metadata["path"]
    )
)

pw.io.jsonlines.write(
    resumes_detected,
    os.path.join(OUTPUT_DIR, "resumes_detected.jsonl")
)

pw.io.jsonlines.write(
    jobs_detected,
    os.path.join(OUTPUT_DIR, "jobs_detected.jsonl")
)

pw.io.jsonlines.write(
    feedback_detected,
    os.path.join(OUTPUT_DIR, "feedback_detected.jsonl")
)

log("Pipeline defined. Starting engine...")
log("Waiting for files...")

pw.run(monitoring_level=pw.MonitoringLevel.NONE)