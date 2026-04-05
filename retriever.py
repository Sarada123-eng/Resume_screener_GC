from pathway.xpacks.llm.vector_store import VectorStoreClient
from config import VECTOR_STORE_PORT
from logger import log_error


def retrieve_candidates(job_query: str, top_k: int = 20) -> list:
    client = VectorStoreClient(
    host="localhost",
    port=VECTOR_STORE_PORT,
    timeout=30,   # ← increase from default 15s
)
    try:
        results = client.query(job_query, k=top_k)
        output = []
        for r in results:
            candidate_id = r["metadata"].get("candidate_id", "unknown")
            dist = r.get("dist", 1.0)
            vector_score = 1.0 - dist
            output.append((candidate_id, vector_score))
        output.sort(key=lambda x: -x[1])
        return output
    except Exception as e:
        log_error(f"Vector store query failed: {e}")
        return []