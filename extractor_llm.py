import json
import os
from groq import Groq
from config import GROQ_API_KEY, LLM_EXTRACTION_MODEL, PROCESSED_DIR
from logger import log, log_resume_extracted, log_warning, log_error

client = Groq(api_key=GROQ_API_KEY)
os.makedirs(PROCESSED_DIR, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_skills(skills: list) -> list:
    if not isinstance(skills, list):
        return []
    return [str(s).lower().strip() for s in skills if s]


def _normalize_list(items) -> list:
    if not isinstance(items, list):
        return []
    return [str(s).strip() for s in items if s and str(s).strip()]


def _save_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Prompts ───────────────────────────────────────────────────────────────────

RESUME_SYSTEM_PROMPT = """You are a resume parser. Extract structured information from the resume text.
Return ONLY a valid JSON object with exactly these fields and no others:
{
  "name": "Full Name",
  "skills": ["skill1", "skill2"],
  "experience_years": 0,
  "role": "job role",
  "education": "degree and institution",
  "projects": ["project name or short description"],
  "certifications": ["cert name"]
}
Rules:
- skills must be a FLAT list of lowercase strings. NOT a dict. NOT nested.
- projects must be a FLAT list of short strings
- certifications must be a FLAT list of short strings
- experience_years must be an integer (0 if unclear)
- role must be a short lowercase string (e.g. "ml engineer")
- Return ONLY the JSON object. No explanation. No markdown. No backticks. No extra fields."""

JD_SYSTEM_PROMPT = """You are a job description parser. Extract structured information from the job description text.
Return ONLY a valid JSON object with exactly these fields:
{
  "required_skills": ["skill1", "skill2"],
  "optional_skills": ["skill3", "skill4"],
  "min_experience": 0,
  "role": "job role"
}
Rules:
- required_skills = MUST HAVE skills
- optional_skills = good-to-have / preferred / plus
- all skills lowercase
- min_experience must be an integer (0 if not specified)
- role must be a short lowercase string (e.g. "ml engineer", "data analyst")
- Return ONLY JSON. No explanation. No markdown. No backticks."""


# ── Resume extraction ─────────────────────────────────────────────────────────

def extract_resume(candidate_id: str, resume_text: str) -> dict:
    try:
        completion = client.chat.completions.create(
            model=LLM_EXTRACTION_MODEL,
            messages=[
                {"role": "system", "content": RESUME_SYSTEM_PROMPT},
                {"role": "user", "content": resume_text},
            ],
            temperature=0,
            max_completion_tokens=2048,
            stream=False,
        )
        msg = completion.choices[0].message
        raw = (msg.content or "").strip()
        if not raw:
            raw = (getattr(msg, "reasoning_content", "") or "").strip()
        data = json.loads(raw)  # ← outside the if block

        # ── Normalize all fields safely ───────────────────────────────────────
        data["skills"] = _normalize_skills(data.get("skills", []))
        data["projects"] = _normalize_list(data.get("projects", []))
        data["certifications"] = _normalize_list(data.get("certifications", []))
        data["candidate_id"] = candidate_id

        # ── candidate_text ────────────────────────────────────────────────────
        projects_text = ", ".join(data["projects"]) if data["projects"] else ""
        data["candidate_text"] = (
            f"Role: {data.get('role', '')} | "
            f"Skills: {', '.join(data.get('skills', []))} | "
            f"Projects: {projects_text} | "
            f"Experience: {data.get('experience_years', 0)} years | "
            f"Education: {data.get('education', '')}"
        )

        out_path = os.path.join(PROCESSED_DIR, f"{candidate_id}.json")
        _save_json(out_path, data)
        log_resume_extracted(candidate_id)
        return data

    except json.JSONDecodeError as e:
        log_warning(f"JSON parse error for resume '{candidate_id}': {e}")
    except Exception as e:
        log_error(f"LLM call failed for resume '{candidate_id}': {e}")

    # ── Fallback ──────────────────────────────────────────────────────────────
    fallback = {
        "candidate_id": candidate_id,
        "name": "",
        "skills": [],
        "experience_years": 0,
        "role": "",
        "education": "",
        "projects": [],
        "certifications": [],
        "candidate_text": "",
    }
    out_path = os.path.join(PROCESSED_DIR, f"{candidate_id}.json")
    _save_json(out_path, fallback)
    return fallback


# ── JD extraction ─────────────────────────────────────────────────────────────

def extract_job(job_id: str, job_text: str) -> dict:
    try:
        completion = client.chat.completions.create(
            model=LLM_EXTRACTION_MODEL,
            messages=[
                {"role": "system", "content": JD_SYSTEM_PROMPT},
                {"role": "user", "content": job_text},
            ],
            temperature=0,
            max_completion_tokens=2048,
            stream=False,
        )
        msg = completion.choices[0].message
        raw = (msg.content or "").strip()
        if not raw:
            raw = (getattr(msg, "reasoning_content", "") or "").strip()
        data = json.loads(raw)  # ← outside the if block

        data["required_skills"] = _normalize_skills(data.get("required_skills", []))
        data["optional_skills"] = _normalize_skills(data.get("optional_skills", []))
        data["job_id"] = job_id

        out_path = os.path.join(PROCESSED_DIR, f"job_{job_id}.json")
        _save_json(out_path, data)
        log(f'Job "{job_id}" extracted successfully')
        return data

    except json.JSONDecodeError as e:
        log_warning(f"JSON parse error for JD '{job_id}': {e}")
    except Exception as e:
        log_error(f"LLM call failed for JD '{job_id}': {e}")

    # ── Fallback ──────────────────────────────────────────────────────────────
    fallback = {
        "job_id": job_id,
        "required_skills": [],
        "optional_skills": [],
        "min_experience": 0,
        "role": "",
    }
    out_path = os.path.join(PROCESSED_DIR, f"job_{job_id}.json")
    _save_json(out_path, fallback)
    return fallback