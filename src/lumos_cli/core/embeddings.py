from __future__ import annotations
import sqlite3, os, httpx, subprocess, re
from typing import List, Tuple
import numpy as np

DB_PATH = os.getenv("LLM_EMBED_DB", ".llm_embeddings.db")

def chunk_code(path: str, content: str):
    """Split code into function/class-level chunks by language."""
    ext = os.path.splitext(path)[1].lower()
    pattern = None

    if ext == ".py":
        pattern = r"(?m)^(def |class )"
    elif ext in (".js", ".ts"):
        pattern = r"(?m)^(function |class |export )"
    elif ext == ".go":
        pattern = r"(?m)^func "
    elif ext in (".ps1", ".psm1"):
        pattern = r"(?m)^function "

    if not pattern:
        return [(path, content)]

    parts = re.split(pattern, content)
    chunks = []
    for i in range(1, len(parts), 2):
        header = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        snippet = header + body
        chunks.append(snippet.strip())

    if not chunks:
        chunks = [content]

    return [(f"{path}::chunk{i}", chunk) for i, chunk in enumerate(chunks)]

class EmbeddingDB:
    def __init__(self, path: str = DB_PATH, model_name: str = "nomic-embed-text"):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.model = model_name
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            path TEXT PRIMARY KEY,
            content TEXT,
            vector BLOB
        )
        """)
        self.conn.commit()

    def _embed(self, text: str) -> np.ndarray:
        payload = {"model": self.model, "input": [text]}
        try:
            with httpx.Client(timeout=60.0) as client:
                r = client.post("http://localhost:11434/api/embed", json=payload)
                r.raise_for_status()
                data = r.json()
            return np.array(data["embeddings"][0], dtype="float32")
        except Exception:
            # Fallback: simple hash-based embedding for basic functionality
            import hashlib
            hash_bytes = hashlib.md5(text.encode()).digest()
            # Convert to float array (basic but functional)
            embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
            # Normalize to unit vector
            return embedding / np.linalg.norm(embedding)

    def add_or_update(self, path: str, content: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM embeddings WHERE path LIKE ?", (f"{path}%",))

        for chunk_path, snippet in chunk_code(path, content):
            vec = self._embed(snippet)
            blob = vec.tobytes()
            cur.execute(
                "INSERT INTO embeddings (path, content, vector) VALUES (?, ?, ?)",
                (chunk_path, snippet, blob)
            )
        self.conn.commit()

    def remove(self, path: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM embeddings WHERE path LIKE ?", (path,))
        self.conn.commit()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        qvec = self._embed(query)
        cur = self.conn.cursor()
        cur.execute("SELECT path, content, vector FROM embeddings")
        rows = cur.fetchall()
        scored = []
        for path, content, blob in rows:
            vec = np.frombuffer(blob, dtype="float32")
            score = float(np.dot(qvec, vec) / (np.linalg.norm(qvec) * np.linalg.norm(vec)))
            scored.append((path, content, score))
        return sorted(scored, key=lambda x: -x[2])[:top_k]

    def get_changed_files(self) -> List[str]:
        try:
            out = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], stderr=subprocess.DEVNULL)
            return out.decode().strip().splitlines()
        except Exception:
            return []
