import pathway as pw
import time
import os

from config import (
    RESUMES_DIR, JOBS_DIR, FEEDBACK_DIR,
    OUTPUT_DIR, PROCESSED_DIR, DEBOUNCE_DELAY
)

from logger import (
    log,
    log_resume_detected,
    log_resume_extracted,
    log_job_detected,
    log_feedback_received,
    log_error
)

from extractor import extract_text_from_pdf, extract_text_from_job
from extractor_llm import extract_resume, extract_job
from indexer import index_candidate, start_vector_store


seen_jobs = set()
seen_resumes = set()
seen_feedback = set()


def get_candidate_id(filepath) -> str:
    filepath = str(filepath).strip('"')
    filename = os.path.basename(filepath)
    return os.path.splitext(filename)[0]


def process_resume_path(path) -> str:
    time.sleep(DEBOUNCE_DELAY)

    filepath = str(path).strip('"')
    candidate_id = get_candidate_id(filepath)

    if candidate_id in seen_resumes:
        return candidate_id

    seen_resumes.add(candidate_id)

    log_resume_detected(candidate_id)

    text = extract_text_from_pdf(filepath)

    if not text:
        log_error(f"Empty text for {candidate_id}")
        return candidate_id

    structured = extract_resume(candidate_id, text)

    if not structured:
        log_error(f"LLM extraction failed for {candidate_id}")
        return candidate_id

    log_resume_extracted(candidate_id)

    candidate_text = structured.get("candidate_text", "")

    if candidate_text:
        index_candidate(candidate_id, candidate_text)
    else:
        log_error(f"No candidate_text for {candidate_id}")

    return candidate_id


def process_job_path(path) -> str:
    time.sleep(DEBOUNCE_DELAY)

    filepath = str(path).strip('"')
    job_id = get_candidate_id(filepath)

    if job_id in seen_jobs:
        return job_id

    seen_jobs.add(job_id)

    log_job_detected(job_id)

    text = extract_text_from_job(filepath)

    if not text:
        log_error(f"Empty job text for {job_id}")
        return job_id

    structured = extract_job(job_id, text)

    if not structured:
        log_error(f"LLM job extraction failed for {job_id}")
        return job_id

    return job_id


def process_feedback_path(path) -> str:
    time.sleep(DEBOUNCE_DELAY)

    feedback_id = get_candidate_id(path)

    if feedback_id in seen_feedback:
        return feedback_id

    seen_feedback.add(feedback_id)

    log_feedback_received(feedback_id)
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


start_vector_store()

log("Pipeline defined. Starting engine...")
log("Waiting for files...")

pw.run(monitoring_level=pw.MonitoringLevel.NONE)