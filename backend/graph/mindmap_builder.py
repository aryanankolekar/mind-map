import json
import networkx as nx
import os

def build_graph(jsonl_path):
    """
    Builds a hierarchical graph from a JSONL file containing structured data.
    Each line in the JSONL file is expected to be a JSON object with 'subject',
    'topic', 'subtopic', 'title', and 'summary' fields.
    """
    G = nx.DiGraph()

    # Check if the file exists and is not empty
    if not os.path.exists(jsonl_path) or os.path.getsize(jsonl_path) == 0:
        print(f"[WARNING] The file {jsonl_path} is empty or does not exist. Returning an empty graph.")
        return G

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                chunk = json.loads(line.strip())
                
                # Extract data with default values for safety
                subject = chunk.get("subject", "General")
                topic = chunk.get("topic", "Miscellaneous")
                subtopic = chunk.get("subtopic", "N/A")
                title = chunk.get("title", "Untitled")
                summary = chunk.get("summary", "")
                text = chunk.get("text", "") # Keep the original text

                # Create nodes with specific types for better identification
                G.add_node(subject, type='subject')
                G.add_node(topic, type='topic', parent=subject)
                G.add_node(subtopic, type='subtopic', parent=topic)
                G.add_node(title, type='chunk', parent=subtopic, summary=summary, text=text)

                # Add edges to form the hierarchy
                G.add_edge(subject, topic)
                G.add_edge(topic, subtopic)
                G.add_edge(subtopic, title)

            except json.JSONDecodeError:
                print(f"[ERROR] Skipping invalid JSON line: {line.strip()}")
                continue
            except KeyError as e:
                print(f"[ERROR] Missing expected key in JSON object: {e}. Line: {line.strip()}")
                continue

    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()

    if node_count > 0:
        print(f"[SUCCESS] Built graph with {node_count} nodes and {edge_count} edges.")
    else:
        print("[INFO] The graph is empty, possibly due to no valid data in the input file.")
        
    return G

def export_graph_to_json(G, filename="mindmap_graph.json"):
    """
    Exports the graph to a JSON file in node-link format.
    """
    from networkx.readwrite import json_graph
    
    # Ensure the output directory exists
    output_dir = os.path.join("data", "processed")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    out_path = os.path.join(output_dir, filename)
    
    try:
        data = json_graph.node_link_data(G)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[SUCCESS] Exported graph JSON to {out_path}")
    except Exception as e:
        print(f"[ERROR] Failed to export graph to JSON: {e}")
