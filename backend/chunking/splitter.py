import re

def simple_split_by_heading(text):
    headings = re.split(r"\n(?=[A-Z][A-Za-z ]{3,}\n)", text)
    return [chunk.strip() for chunk in headings if len(chunk.strip()) > 100]

def sliding_window_chunks(text, max_words=200, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+max_words]
        chunks.append(" ".join(chunk))
        i += max_words - overlap
    return chunks
