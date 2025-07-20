import faiss
import os
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # small & fast

# Index and metadata store
index = faiss.IndexFlatL2(384)
metadata = []

def build_index_from_chunks(jsonl_path):
    with open(jsonl_path, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f]

    texts = [c["summary"] + " " + c["title"] for c in chunks]
    vectors = model.encode(texts)

    global index, metadata
    index.add(vectors)
    metadata = chunks
    print(f"[✓] Indexed {len(chunks)} chunks.")

def search_similar(text, top_k=5):
    vector = model.encode([text])
    distances, indices = index.search(vector, top_k)

    results = []
    for i in indices[0]:
        results.append(metadata[i])
    return results
