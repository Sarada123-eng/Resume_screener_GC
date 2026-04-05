import threading
import time
import pathway as pw
from pathway.io.python import ConnectorSubject
from sentence_transformers import SentenceTransformer
from pathway.xpacks.llm.vector_store import VectorStoreServer, VectorStoreClient
from config import EMBEDDING_MODEL, VECTOR_STORE_HOST, VECTOR_STORE_PORT
from logger import log, log_resume_indexed, log_error

# ── Global singleton ──────────────────────────────────────────────────────────
log("Loading BGE embedding model...")
_model = SentenceTransformer(EMBEDDING_MODEL)
log("BGE embedding model loaded.")

_server = None
_server_thread = None
_subject = None


# ── Embedder UDF ──────────────────────────────────────────────────────────────

@pw.udf
def embed_text(text: str) -> list[float]:
    return _model.encode(text, normalize_embeddings=True).tolist()


# ── Connector Subject (live push) ─────────────────────────────────────────────

class CandidateSubject(ConnectorSubject):
    def run(self):
        while True:
            time.sleep(1)  # keep alive indefinitely


# ── Start Vector Store ────────────────────────────────────────────────────────

def start_vector_store():
    global _server, _server_thread, _subject

    _subject = CandidateSubject()

    table = pw.io.python.read(
        _subject,
        schema=pw.schema_from_types(data=str, _metadata=dict),
    )

    _server = VectorStoreServer(
        table,
        embedder=embed_text,
    )

    _server_thread = threading.Thread(
        target=_server.run_server,
        kwargs={
            "host": VECTOR_STORE_HOST,
            "port": VECTOR_STORE_PORT,
            "threaded": True,
            "with_cache": False,
        },
        daemon=True,
    )
    _server_thread.start()
    log(f"VectorStoreServer started on {VECTOR_STORE_HOST}:{VECTOR_STORE_PORT}")


# ── Index a candidate (live push) ─────────────────────────────────────────────

def index_candidate(candidate_id: str, candidate_text: str):
    global _subject

    if _subject is None:
        log_error("VectorStore not started. Call start_vector_store() first.")
        return

    _subject.next(
        data=candidate_text,
        _metadata={"candidate_id": candidate_id},
    )
    log_resume_indexed(candidate_id)


# ── Retrieve candidates ───────────────────────────────────────────────────────

def retrieve_candidates(job_query: str, top_k: int = 20) -> list:
    client = VectorStoreClient(
        host="localhost",
        port=VECTOR_STORE_PORT,
    )

    try:
        results = client.query(job_query, k=top_k)
        output = []
        for r in results:
            candidate_id = r["metadata"].get("candidate_id", "unknown")
            dist = r.get("dist", 1.0)
            vector_score = 1.0 - dist 
            output.append((candidate_id, vector_score))

        # sort by score descending
        output.sort(key=lambda x: -x[1])
        return output

    except Exception as e:
        log_error(f"Vector store query failed: {e}")
        return []