# AGENT.md — Real-Time RAG Resume Screening System

## 🧠 Project Overview

You are building a real-time AI-powered resume screening system using Pathway and a RAG pipeline.

The system must:

* Continuously ingest resumes and job descriptions
* Extract structured data using LLMs
* Maintain a live vector index
* Dynamically rank candidates based on job descriptions
* Update results instantly when new data arrives

This is a hackathon project. Prioritize:

* stability
* clarity
* demo visibility

---

## 🧱 Architecture (STRICT — DO NOT CHANGE)

The system is divided into components:

1. Config Layer
2. Data Layer (Pathway ingestion)
3. Extraction Layer (LLM → structured JSON)
4. Indexing Layer (embeddings + vector DB)
5. Ranking Layer (retrieval + reranking + explanation)
6. UI Layer (Streamlit)

You MUST:

* implement components in order
* keep modules separate
* avoid merging logic across layers

---

## ⚙️ Core Technologies

* Pathway → real-time ingestion and indexing
* PyMuPDF → PDF parsing
* BGE-base → embeddings
* BGE cross-encoder → reranking
* LLM (Claude/OpenAI) → extraction + explanation
* Streamlit → UI

Do NOT replace these without instruction.

---

## 🔄 Development Rules

1. Build ONE component at a time.

2. Do NOT implement future components early.

3. Each component must be:

   * complete
   * testable
   * working independently

4. After each step:

   * ensure code runs
   * verify output manually

---

## 🚫 Strict Constraints

* Do NOT redesign architecture
* Do NOT introduce new frameworks
* Do NOT use LangChain unless explicitly asked
* Do NOT combine multiple components into one file
* Do NOT over-engineer

---

## 🧠 Data Flow (REFERENCE)

Resume/JD file added
→ Pathway detects
→ Extraction layer processes text
→ Structured JSON stored
→ Embedding created
→ Stored in vector DB
→ Ranking triggered
→ UI updates

---

## 🎯 Ranking Logic (MANDATORY)

* Step 1: vector retrieval (top K)
* Step 2: cross-encoder reranking
* Step 3: hybrid score (0.7 / 0.3)
* Step 4: skill matching
* Step 5: LLM explanation with fallback

---

## 🖥️ UI Behavior

* Display ranked candidates
* Show:

  * scores
  * matched skills
  * missing skills
  * explanation
* Show rank changes (NEW, ↑, ↓)
* Auto-refresh every 5 seconds

---

## 🧪 Testing Philosophy

* Prefer simple, predictable inputs
* Avoid edge-case complexity initially
* Ensure deterministic outputs

---

## ⚡ Performance Constraints

* Use batching where possible
* Avoid blocking calls
* Add timeouts to all LLM calls
* Ensure system responds within a few seconds

---

## 🧾 Logging Requirements

All major actions must log:

Format:
[HH:MM:SS] Event description

Examples:

* Resume detected
* Extraction complete
* Index updated
* Ranking updated

---

## 🏆 Goal

Deliver a working, real-time system that clearly demonstrates:

* live ingestion
* dynamic ranking
* explainable results

The demo must be smooth, fast, and visually clear.

---

## 🔒 Final Rule

You are an assistant, not the architect.

Follow the provided design exactly.
Do not improvise system-level decisions.
