from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json

from ingestion.pdf_loader import extract_text_from_pdf
from ingestion.image_ocr import extract_text_from_image
from ingestion.youtube_transcriber import extract_transcript
from ingestion.social_scraper import extract_text_from_link
from preprocessing.cleaner import clean_text
from chunking.labeler import label_chunk
from utils.graph import update_graph

app = Flask(__name__)
CORS(app)

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/raw"))
PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
LABELED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/labeled"))
GRAPH_PATH = os.path.join(PROCESSED_DIR, "mindmap_graph.json")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(LABELED_DIR, exist_ok=True)


@app.route("/")
def home():
    return "🧠 MindMap Backend Running"


@app.route("/api/ingest", methods=["POST"])
def ingest():
    source_type = request.form.get("type")
    text = None
    filename = None

    try:
        # FILE
        if source_type == "file":
            uploaded_file = request.files.get("file")
            if not uploaded_file:
                return jsonify({"status": "error", "message": "No file uploaded"}), 400

            filename = uploaded_file.filename
            ext = filename.lower().split(".")[-1]
            raw_path = os.path.join(RAW_DIR, filename)
            uploaded_file.save(raw_path)
            print(f"[✓] File saved to {raw_path}")

            if ext == "pdf":
                text = extract_text_from_pdf(raw_path)
            elif ext in ["jpg", "jpeg", "png"]:
                text = extract_text_from_image(raw_path)
            else:
                return jsonify({"status": "error", "message": "Unsupported file type"}), 400

        # LINK
        elif source_type == "link":
            link = request.form.get("link")
            if "youtube.com" in link or "youtu.be" in link:
                text = extract_transcript(link)
                filename = f"youtube_{uuid.uuid4().hex[:8]}.txt"
            else:
                text = extract_text_from_link(link)
                filename = f"link_{uuid.uuid4().hex[:8]}.txt"
        else:
            return jsonify({"status": "error", "message": "Invalid type"}), 400

        # Cleaning + Saving
        if not text:
            return jsonify({"status": "error", "message": "No text extracted"}), 500

        cleaned = clean_text(text)
        processed_path = os.path.join(PROCESSED_DIR, filename)
        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"[✓] Cleaned text saved to {processed_path}")

        # Labeling
        print("[DEBUG] calling label_chunk()")
        chunks = label_chunk(cleaned)
        print(f"[DEBUG] label_chunk() returned {len(chunks)} chunks")

        labeled_path = os.path.join(LABELED_DIR, filename.replace(".txt", "_labeled.jsonl"))
        with open(labeled_path, "w", encoding="utf-8") as f:
            for chunk in chunks:
                json.dump(chunk, f)
                f.write("\n")
        # Update graph
        update_graph(labeled_path, GRAPH_PATH)
        print(f"[✓] Graph updated: {GRAPH_PATH}")

        return jsonify({
            "status": "success",
            "filename": filename,
            "summary": cleaned[:500] + "..." if len(cleaned) > 500 else cleaned
        })

    except Exception as e:
        print(f"[✗] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/graph", methods=["GET"])
def get_graph():
    try:
        return send_file(GRAPH_PATH)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/api/topics", methods=["GET"])
def get_topics():
    labeled_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/labeled"))
    topics = set()

    try:
        for filename in os.listdir(labeled_dir):
            if filename.endswith(".jsonl"):
                with open(os.path.join(labeled_dir, filename), "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            obj = json.loads(line)
                            if "label" in obj:
                                topics.add(obj["label"])
                        except:
                            continue
        return jsonify(sorted(list(topics)))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/topic/<label>", methods=["GET"])
def get_topic(label):
    labeled_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/labeled"))
    label = label.strip()
    summaries = []

    try:
        for filename in os.listdir(labeled_dir):
            if filename.endswith(".jsonl"):
                with open(os.path.join(labeled_dir, filename), "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            obj = json.loads(line)
                            if obj.get("label") == label and obj.get("summary"):
                                summaries.append(obj["summary"])
                        except:
                            continue

        if not summaries:
            return jsonify({"status": "error", "message": "Topic not found"}), 404

        # Simple summary and key points extraction
        full_summary = " ".join(summaries)
        key_points = [s.strip().split(".")[0] for s in summaries[:5] if "." in s][:3]

        return jsonify({
            "label": label,
            "summary": full_summary,
            "keyPoints": key_points
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/resources", methods=["GET"])
def find_resources():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])

    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/raw"))
    found_files = []
    try:
        for filename in os.listdir(raw_dir):
            if query in filename.lower():
                # Simple type detection from extension
                ext = filename.split(".")[-1]
                if ext in ["pdf", "txt", "docx", "mp4", "jpg", "png"]:
                    file_type = ext
                else:
                    file_type = "file"
                
                found_files.append({"name": filename, "type": file_type})
        return jsonify(found_files)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
