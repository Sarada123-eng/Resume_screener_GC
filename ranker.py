from logger import log, log_warning, log_ranking_updated
import os
import json
from config import (
    PROCESSED_DIR,
    TOP_K_RETRIEVAL,
    HYBRID_WEIGHT_RERANKER,
    HYBRID_WEIGHT_VECTOR,
    RERANKER_MODEL,
    GROQ_API_KEY,
    LLM_MODEL,
    GPT_TIMEOUT
)
from retriever import retrieve_candidates
from sentence_transformers import CrossEncoder
from groq import Groq

# ─────────────────────────────────────────────
# INIT MODELS
# ─────────────────────────────────────────────
log("Loading BGE reranker model...")
_reranker = CrossEncoder(RERANKER_MODEL)
log("BGE reranker model loaded.")

_llm_client = Groq(api_key=GROQ_API_KEY)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _load_candidate(candidate_id: str):
    path = os.path.join(PROCESSED_DIR, f"{candidate_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _skill_intersection(candidate_skills, required_skills):
    candidate_set = set([s.lower() for s in candidate_skills])
    required_set = set([s.lower() for s in required_skills])
    matched = sorted(candidate_set & required_set)
    missing = sorted(required_set - candidate_set)
    return matched, missing


def _extract_skills_from_text(text: str):
    known_skills = [
        "python", "pytorch", "tensorflow",
        "machine learning", "deep learning",
        "scikit-learn", "sql", "docker", "kubernetes"
    ]
    text = text.lower()
    return [s for s in known_skills if s in text]


# ─────────────────────────────────────────────
# GPT EXPLANATION
# ─────────────────────────────────────────────
def _generate_explanation(candidate: dict, job_desc: str) -> str:
    name = candidate.get("name", candidate["candidate_id"])
    matched = candidate.get("matched_skills", [])
    missing = candidate.get("missing_skills", [])
    years = candidate.get("experience_years", 0)
    projects = candidate.get("projects", [])
    certs = candidate.get("certifications", [])

    prompt = (
        f"Job Description: {job_desc[:300]}\n\n"
        f"Candidate: {name}\n"
        f"Matched skills: {', '.join(matched)}\n"
        f"Missing skills: {', '.join(missing)}\n"
        f"Experience: {years} years\n"
        f"Projects: {', '.join(projects) if projects else 'none'}\n"
        f"Certifications: {', '.join(certs) if certs else 'none'}\n\n"
        f"Write exactly 2 sentences explaining why this candidate is or isn't a good fit."
    )

    try:
        completion = _llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_completion_tokens=200,
            timeout=GPT_TIMEOUT,
        )
        msg = completion.choices[0].message
        text = ""
        for attr in ["content", "reasoning_content"]:
            val = getattr(msg, attr, None)
            if val and isinstance(val, str) and val.strip():
                text = val.strip()
                break
        if text:
            return text

    except Exception:
        pass

    return (
        f"{name} matches {len(matched)} required skills "
        f"and is missing {len(missing)}. "
        f"Has {years} years of experience."
    )


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────
def rank_candidates(job_desc: str, candidate_ids: list, required_skills: list = [], optional_skills: list = []):

    if not job_desc or not job_desc.strip():
        log_warning("Empty job description")
        return []

    if not candidate_ids:
        log_warning("No candidates provided")
        return []

    log(f"Ranking {len(candidate_ids)} candidates...")

    if not required_skills:
        required_skills = _extract_skills_from_text(job_desc)

    if not optional_skills:
        optional_skills = []

    # ── Stage 1: Vector retrieval ─────────────────────────────────────────────
    vector_results = retrieve_candidates(job_desc, top_k=TOP_K_RETRIEVAL)

    if not vector_results:
        log_warning("Vector store returned no results")
        return []

    candidates = []
    for candidate_id, vector_score in vector_results:
        data = _load_candidate(candidate_id)
        if data is None:
            log_warning(f"Missing JSON for {candidate_id}")
            continue
        data["vector_score"] = vector_score
        candidates.append(data)

    # ── Stage 2: Cross-encoder ────────────────────────────────────────────────
    pairs = [[job_desc, c["candidate_text"]] for c in candidates]
    rerank_scores = _reranker.predict(pairs)

    for i, c in enumerate(candidates):
        c["rerank_score"] = float(rerank_scores[i])

    # ── Hybrid score + projects + certs + experience ──────────────────────────
    for c in candidates:
        # safe access — works for old JSONs without these fields too
        projects = c.get("projects", []) or []
        certs = c.get("certifications", []) or []
        experience = c.get("experience_years", 0) or 0
        candidate_skills = set([s.lower() for s in (c.get("skills", []) or [])])

        exp_score = min(experience / 5, 1.0)
        project_score = min(len(projects) * 0.05, 0.2)
        cert_score = min(len(certs) * 0.03, 0.1)
        opt_match = len(candidate_skills & set(optional_skills))
        opt_score = opt_match / max(len(optional_skills), 1)

        c["final_score"] = round(
            HYBRID_WEIGHT_RERANKER * c["rerank_score"] +
            HYBRID_WEIGHT_VECTOR * c["vector_score"] +
            0.1 * exp_score +
            0.05 * opt_score +
            project_score +
            cert_score,
            4
        )

    # ── Sort ──────────────────────────────────────────────────────────────────
    candidates = sorted(
        candidates,
        key=lambda x: (-x["final_score"], x["candidate_id"])
    )

    # ── Skill intersection ────────────────────────────────────────────────────
    for c in candidates:
        matched, missing = _skill_intersection(
            c.get("skills", []) or [],
            required_skills
        )
        c["matched_skills"] = matched
        c["missing_skills"] = missing

    # ── GPT explanation ───────────────────────────────────────────────────────
    for c in candidates:
        c["reason"] = _generate_explanation(c, job_desc)
    
    log_ranking_updated("resume_added / JD_changed")
    return candidates