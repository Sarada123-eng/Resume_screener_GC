import streamlit as st
import os
import json
import hashlib
from datetime import datetime
from config import PROCESSED_DIR, UI_REFRESH_INTERVAL

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #111827;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    margin-bottom: 15px;
}
.top-card {
    border: 2px solid #22c55e;
}
.skill-match {
    color: #22c55e;
    font-weight: bold;
}
.skill-miss {
    color: #ef4444;
}
.score {
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 AI Resume Screener")


def _get_index_hash() -> str:
    """Hash of current indexed candidates — changes when new resume added."""
    if not os.path.exists(PROCESSED_DIR):
        return ""
    files = sorted([
        f for f in os.listdir(PROCESSED_DIR)
        if f.endswith(".json") and not f.startswith("job_")
    ])
    return hashlib.md5(str(files).encode()).hexdigest()


current_hash = _get_index_hash()
if "index_hash" not in st.session_state:
    st.session_state["index_hash"] = current_hash

if current_hash != st.session_state["index_hash"]:
    st.session_state["index_hash"] = current_hash
    st.toast("🆕 New resume detected — refresh rankings!", icon="📄")
    st.rerun()


def load_all_candidates() -> list:
    candidates = []
    if not os.path.exists(PROCESSED_DIR):
        return candidates
    for fname in os.listdir(PROCESSED_DIR):
        if fname.endswith(".json") and not fname.startswith("job_"):
            path = os.path.join(PROCESSED_DIR, fname)
            with open(path, "r") as f:
                candidates.append(json.load(f))
    return candidates


left, right = st.columns([1, 2])


with left:
    st.subheader("📄 Job Description")

    job_desc = st.text_area(
        "Paste job description",
        height=250,
        placeholder="e.g. Looking for ML Engineer with Python, PyTorch..."
    )

    if job_desc.strip():
        st.success(f"✅ JD loaded — {len(job_desc.split())} words")
    else:
        st.warning("⚠️ Please enter a job description to start ranking.")

    st.markdown("---")
    st.subheader("📤 Upload Resume")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded:
        os.makedirs("data/resumes", exist_ok=True)
        save_path = os.path.join("data", "resumes", uploaded.name)
        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"✅ Uploaded: `{uploaded.name}`")
        st.info("⏳ Pipeline will detect and index it automatically.")

    st.markdown("---")

    candidates_on_disk = load_all_candidates()
    st.metric("Resumes Indexed", len(candidates_on_disk))

    last_updated = st.session_state.get("last_updated", "—")
    st.caption(f"Last ranked: {last_updated}")


with right:
    st.subheader("🏆 Ranked Candidates")

    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        rank_clicked = st.button("🚀 Rank Candidates", type="primary")

    with col_btn2:
        if st.button("🔄 Refresh"):
            st.rerun()

    if rank_clicked:
        if not job_desc.strip():
            st.warning("⚠️ Enter a job description first.")
        else:
            candidates = load_all_candidates()
            if not candidates:
                st.warning("No resumes indexed yet. Upload resumes first.")
            else:
                with st.spinner("🔍 Extracting JD + Ranking..."):
                    from extractor_llm import extract_job
                    job_id = "live_" + hashlib.md5(job_desc.encode()).hexdigest()[:8]
                    job_data = extract_job(job_id, job_desc)

                    required_skills = job_data.get("required_skills", [])
                    optional_skills = job_data.get("optional_skills", [])
                    candidate_ids = [c["candidate_id"] for c in candidates]

                    from ranker import rank_candidates
                    ranked = rank_candidates(
                        job_desc,
                        candidate_ids,
                        required_skills=required_skills,
                        optional_skills=optional_skills,
                    )

                    prev_ranked = st.session_state.get("ranked", [])
                    prev_positions = {
                        c["candidate_id"]: i for i, c in enumerate(prev_ranked)
                    }
                    st.session_state["prev_positions"] = prev_positions
                    st.session_state["ranked"] = ranked
                    st.session_state["last_updated"] = datetime.now().strftime("%H:%M:%S")

    ranked = st.session_state.get("ranked", [])
    prev_positions = st.session_state.get("prev_positions", {})

    if not ranked:
        st.info("Click **🚀 Rank Candidates** to see results.")
    else:
        st.caption(f"Showing {len(ranked)} candidates")

        for i, c in enumerate(ranked):
            is_top = i == 0
            card_class = "card top-card" if is_top else "card"
            candidate_id = c["candidate_id"]

            if candidate_id not in prev_positions:
                indicator = "🆕 NEW"
                indicator_color = "#facc15"
            elif prev_positions[candidate_id] > i:
                delta = prev_positions[candidate_id] - i
                indicator = f"🟢 ↑{delta}"
                indicator_color = "#22c55e"
            elif prev_positions[candidate_id] < i:
                delta = i - prev_positions[candidate_id]
                indicator = f"🔴 ↓{delta}"
                indicator_color = "#ef4444"
            else:
                indicator = ""
                indicator_color = ""

            badge = (
                f"<span style='font-size:14px; color:{indicator_color}; "
                f"margin-left:10px'>{indicator}</span>"
                if indicator else ""
            )

            with st.container():
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

                st.markdown(
                    f"### #{i+1} {c.get('name', candidate_id).title()}{badge}",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div class='score'>Final Score: {c['final_score']:.3f}</div>",
                    unsafe_allow_html=True
                )
                st.progress(min(max(c["final_score"], 0.0), 1.0))

                col1, col2, col3 = st.columns(3)
                col1.metric("Vector", f"{c['vector_score']:.3f}")
                col2.metric("Rerank", f"{c['rerank_score']:.3f}")
                col3.metric("Experience", f"{c.get('experience_years', 0)} yrs")

                projects = c.get("projects", []) or []
                certs = c.get("certifications", []) or []

                if projects:
                    st.markdown("**Projects:**")
                    for p in projects:
                        st.markdown(f"&nbsp;&nbsp;📌 {p}", unsafe_allow_html=True)

                if certs:
                    st.markdown("**Certifications:**")
                    for cert in certs:
                        st.markdown(f"&nbsp;&nbsp;🏅 {cert}", unsafe_allow_html=True)

                if c.get("matched_skills"):
                    st.markdown("**Matched Skills:**")
                    st.markdown(
                        " ".join([
                            f"<span class='skill-match'>✔ {s}</span>"
                            for s in c["matched_skills"]
                        ]),
                        unsafe_allow_html=True
                    )

                if c.get("missing_skills"):
                    st.markdown("**Missing Skills:**")
                    st.markdown(
                        " ".join([
                            f"<span class='skill-miss'>✘ {s}</span>"
                            for s in c["missing_skills"]
                        ]),
                        unsafe_allow_html=True
                    )

                if c.get("reason"):
                    with st.expander("💡 Why this candidate?"):
                        st.info(c["reason"])

                st.markdown("</div>", unsafe_allow_html=True)