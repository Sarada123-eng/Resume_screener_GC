# 🧠 Real-Time AI Resume Screener
### GC ML Hackathon 2026 — Powered by Pathway + Groq + BGE

A real-time AI-powered resume screening system that continuously ingests resumes and job descriptions, dynamically ranks candidates using hybrid semantic search, and explains every decision in plain English — with zero manual reprocessing.

---

## 📽️ Demo Video

> [Insert demo video link here]

---

## Linux environment is a must for running this application as pathway don't support window

## 🏗️ Architecture

```
data/resumes/         data/jobs/          data/feedback/
      │                    │                     │
      └────────────────────┴─────────────────────┘
                           │
                    Pathway Streaming
                    pw.io.fs.read()
                           │
              ┌────────────┴────────────┐
              │                         │
         PyMuPDF                   Plaintext
       PDF Extractor              JD Extractor
              │                         │
              └────────────┬────────────┘
                           │
                    Groq LLM (gpt-oss-120b)
                    Structured JSON Extraction
                    {name, skills, experience,
                     projects, certifications}
                           │
                    BGE-base-en-v1.5
                    Embedding (768-dim)
                           │
                    Pathway VectorStoreServer
                    (port 8666, live push)
                           │
                    ┌──────┴──────┐
                    │             │
              Vector Search   Cross-Encoder
              (top 20)        BGE-reranker-large
                    │             │
                    └──────┬──────┘
                           │
                    Hybrid Score
                    0.7×rerank + 0.3×vector
                    + experience + projects
                    + certifications
                           │
                    Groq LLM Explanation
                    (RAG-grounded, no hallucination)
                           │
                    Streamlit Dashboard
```

---

## ✨ Key Features

- **Real-Time Ingestion** — Pathway watches 3 folders simultaneously: resumes, jobs, feedback
- **LLM Extraction** — Groq extracts structured JSON from raw PDFs in ~2 seconds
- **Live Vector Indexing** — BGE embeddings pushed to Pathway VectorStoreServer without restart
- **Hybrid Ranking** — Vector similarity + cross-encoder reranking + experience + projects + certifications
- **RAG Explanations** — Every ranking decision explained using retrieved candidate data
- **Rank Change Indicators** — 🆕 NEW, 🟢 ↑N, 🔴 ↓N shown on every re-rank
- **Auto-Detection** — Upload a resume → pipeline detects → indexes → UI notifies automatically

---

## 📁 Project Structure

```
Resume_screener_GC/
│
├── data/
│   ├── resumes/          # Drop PDF resumes here
│   ├── jobs/             # Drop JD .txt files here
│   └── feedback/         # Drop feedback .txt files here
│
├── processed/            # Extracted JSON per candidate
├── output/               # Pipeline logs + detected JSONL files
│
├── pipeline.py           # Main Pathway streaming pipeline
├── extractor.py          # PDF + plaintext text extraction
├── extractor_llm.py      # Groq LLM structured extraction
├── indexer.py            # BGE embeddings + Pathway VectorStore
├── retriever.py          # VectorStoreClient query (no model loading)
├── ranker.py             # Hybrid ranking + GPT explanation
├── app.py                # Streamlit UI
├── logger.py             # Structured logging
├── config.py             # All constants and paths
├── create_sample_data.py # Generate sample resumes
│
├── .env                  # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-repo/resume-screener.git
cd resume-screener
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ First run will download BGE embedding model (~438MB) and BGE reranker model (~2.24GB). This takes a few minutes on first launch only.

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
VECTOR_STORE_PORT=8666
```

Get your free Groq API key at: https://console.groq.com

### 5. Create sample data (optional)

```bash
python create_sample_data.py
```

This generates 10 sample resumes (PDF) across 3 roles and 3 job descriptions.

---

## 🚀 Running the System

The system requires **two terminals running simultaneously**.

### Terminal 1 — Start the Pipeline

```bash
source venv/bin/activate
python pipeline.py
```

Wait until you see:
```
[HH:MM:SS] INFO: BGE embedding model loaded.
[HH:MM:SS] INFO: VectorStoreServer started on 0.0.0.0:8666
[HH:MM:SS] INFO: Waiting for files...
======== Running on http://0.0.0.0:8666 ========
```

The pipeline will automatically detect and index all existing resumes in `data/resumes/`.

### Terminal 2 — Start the UI

```bash
source venv/bin/activate
streamlit run app.py
```

Open your browser at: `http://localhost:8501`

> ⚠️ Always start `pipeline.py` **before** `app.py`. The UI queries the vector store which only exists when the pipeline is running.

---

## 🎮 How to Use

### Rank existing resumes
1. Paste a job description in the left panel
2. Click **🚀 Rank Candidates**
3. View ranked candidates with scores, skill badges, and explanations

### Upload a new resume
1. Click **Browse files** in the Upload Resume section
2. Select a PDF resume
3. The pipeline detects it automatically (~2-3 seconds)
4. A toast notification appears: `🆕 New resume detected!`
5. Click **🚀 Rank Candidates** to see updated rankings with `🆕 NEW` badge

### Add a job description file
Drop a `.txt` file into `data/jobs/` — the pipeline detects and extracts it automatically.

### Add recruiter feedback
Drop a `.txt` file into `data/feedback/` — logged in real time with timestamp.

---

## 📊 Scoring Formula

```
final_score = 0.7 × rerank_score          (BGE cross-encoder)
            + 0.3 × vector_score           (BGE embedding similarity)
            + 0.1 × exp_score              (experience years, capped at 5+)
            + 0.05 × optional_skill_score  (nice-to-have skills match)
            + project_score                (0.05 per project, max 0.20)
            + cert_score                   (0.03 per cert, max 0.10)
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Streaming Engine | [Pathway](https://pathway.com) |
| PDF Extraction | PyMuPDF (fitz) |
| LLM Extraction + Explanation | Groq — openai/gpt-oss-120b |
| Embedding Model | BAAI/BGE-base-en-v1.5 (768-dim) |
| Vector Store | Pathway VectorStoreServer |
| Reranker | BAAI/BGE-reranker-large |
| UI | Streamlit |
| Language | Python 3.10 |

---

## 📋 Evaluation Criteria Coverage

| Criterion | Weight | Implementation |
|-----------|--------|---------------|
| Real-Time Data Ingestion | 30% | Pathway streams 3 folders, debounce, dedup, live push |
| Adaptive Ranking System | 25% | Hybrid score, cross-encoder, deterministic sort |
| RAG Reasoning Quality | 25% | Retrieved JSON grounded explanations, skill intersection |
| System Design & UI | 10% | 6 modular components, Streamlit dashboard |
| Presentation & Demo | 10% | Slides + demo video |

---

## 🔧 Configuration

All constants are in `config.py`:

```python
DEBOUNCE_DELAY = 2          # seconds before processing a detected file
TOP_K_RETRIEVAL = 20        # candidates retrieved from vector store
HYBRID_WEIGHT_RERANKER = 0.7
HYBRID_WEIGHT_VECTOR = 0.3
GPT_TIMEOUT = 3             # seconds before falling back to template
UI_REFRESH_INTERVAL = 5     # seconds between auto-refresh checks
VECTOR_STORE_PORT = 8666
```

---

## 📝 Logs

All pipeline events are logged to `output/pipeline.log`:

```
[HH:MM:SS] INFO: Resume "alice_ml.pdf" detected
[HH:MM:SS] INFO: Resume "alice_ml" extracted successfully
[HH:MM:SS] INFO: Resume "alice_ml" embedded and indexed
[HH:MM:SS] INFO: Ranking updated — trigger: resume_added / JD_changed
```

---

## 👥 Team

| Name | Role |
|------|------|
| [Name 1] | [Role] |
| [Name 2] | [Role] |
| [Name 3] | [Role] |
| [Name 4] | [Role] |

---

## 📚 References

- [Pathway Documentation](https://pathway.com/developers)
- [BGE Embedding Models](https://huggingface.co/BAAI/bge-base-en-v1.5)
- [BGE Reranker](https://huggingface.co/BAAI/bge-reranker-large)
- [Groq API](https://console.groq.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.
- Nogueira & Cho (2019). Passage Re-ranking with BERT. arXiv:1901.04085.