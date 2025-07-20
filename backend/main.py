from ingestion.pdf_loader import extract_text_from_pdf
from ingestion.image_ocr import extract_text_from_image
from ingestion.youtube_transcriber import extract_transcript
from ingestion.social_scraper import extract_text_from_link
from preprocessing.cleaner import clean_text
from chunking.labeler import label_chunk
from graph.mindmap_builder import build_graph, export_graph_to_json
from memory.embedding_store import build_index_from_chunks, search_similar
import os
import json
import uuid

def ingest_resource(source_type, path_or_url):
    """Ingest resource from a given source type and path/url."""
    print(f"[INFO] Ingesting {source_type} from {path_or_url}...")
    if source_type == "pdf":
        raw_text = extract_text_from_pdf(path_or_url)
    elif source_type == "image":
        raw_text = extract_text_from_image(path_or_url)
    elif source_type == "youtube":
        raw_text = extract_transcript(path_or_url)
    elif source_type == "link":
        raw_text = extract_text_from_link(path_or_url)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
    
    cleaned_text = clean_text(raw_text)
    print(f"[SUCCESS] Ingestion complete. Extracted and cleaned {len(cleaned_text)} characters.")
    return cleaned_text

def save_labeled_data(labeled_chunks, filename):
    """Saves the labeled data to a JSONL file."""
    out_dir = os.path.join("data", "labeled")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{filename}_labeled.jsonl")
    
    with open(out_path, "w", encoding="utf-8") as f:
        for entry in labeled_chunks:
            f.write(json.dumps(entry) + "\n")
    print(f"[SUCCESS] Saved labeled data to {out_path}")
    return out_path

def process_and_build_mindmap(source_type, path_or_url):
    """Main pipeline to process a resource and build a mind map."""
    
    # Generate a unique filename
    filename = f"{source_type}_{str(uuid.uuid4())[:8]}"

    # Step 1: Ingest and clean the text
    text = ingest_resource(source_type, path_or_url)
    if not text or len(text.strip()) < 100:
        print("[ERROR] Ingested text is too short or empty. Aborting.")
        return

    # Step 2: Label and chunk the text using the new generative model
    # This now handles chunking, summarization, and hierarchical labeling
    print("\n[INFO] Starting chunking and labeling process...")
    labeled_data = label_chunk(text)
    if not labeled_data:
        print("[ERROR] No data was labeled. Cannot proceed.")
        return
    
    # Step 3: Save the structured data
    jsonl_path = save_labeled_data(labeled_data, filename)
    print(f"[INFO] Labeled data saved to {jsonl_path}")

    # Step 4: Build and export the knowledge graph
    print("\n[INFO] Building knowledge graph...")
    G = build_graph(jsonl_path)
    if G.number_of_nodes() > 0:
        export_graph_to_json(G, f"{filename}_mindmap.json")
    else:
        print("[WARNING] Graph is empty. Skipping export.")

    # Step 5: (Optional) Build semantic memory for search
    print("\n[INFO] Building semantic memory index...")
    build_index_from_chunks(jsonl_path)
    print("[SUCCESS] Semantic index built.")

if __name__ == "__main__":
    # --- Configuration ---
    # Choose one of the following source types: "youtube", "pdf", "link", "image"
    SOURCE_TYPE = "youtube"
    
    # Provide the corresponding path or URL
    # For YouTube: "https://www.youtube.com/watch?v=your_video_id"
    # For PDF: "data/raw/your_document.pdf"
    # For Web Link: "https://example.com/article"
    # For Image: "data/raw/your_image.png"
    INPUT_PATH = "https://www.youtube.com/watch?v=Gx5qb1uHss4"
    
    # --- Execution ---
    process_and_build_mindmap(SOURCE_TYPE, INPUT_PATH)

    # --- Example Search Query ---
    # You can test the search functionality after the pipeline runs
    query = "What are the key principles of deep learning mentioned?"
    print(f"\n[INFO] Performing a test search for: '{query}'")
    search_results = search_similar(query)
    
    if search_results:
        print("[SUCCESS] Found search results:")
        for res in search_results:
            print(f"  - Title: {res.get('title', 'N/A')}, Summary: {res.get('summary', 'N/A')[:100]}...")
    else:
        print("[INFO] No relevant results found for the query.")
