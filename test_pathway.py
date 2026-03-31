import pathway as pw
import os
from config import RESUMES_DIR, OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

resumes_raw = pw.io.fs.read(
    RESUMES_DIR,
    format="binary",
    mode="streaming",
    with_metadata=True
)

# Just select path directly, no pw.apply at all
result = resumes_raw.select(
    path=pw.this._metadata["path"]
)

pw.io.jsonlines.write(
    result,
    os.path.join(OUTPUT_DIR, "test_output.jsonl")
)

pw.run()
