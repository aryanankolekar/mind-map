import json
import os

print("[DEBUG] ✅ using UPDATED graph.py")


def update_graph(labeled_path, graph_path):
    nodes = []
    links = []

    # Load existing graph if it exists
    if os.path.exists(graph_path):
        with open(graph_path, "r", encoding="utf-8") as f:
            graph = json.load(f)
            nodes = graph.get("nodes", [])
            links = graph.get("links", [])

    existing_labels = {node["id"] for node in nodes}
    new_nodes = []

    # Read labeled .jsonl file
    with open(labeled_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                label = obj.get("label", "").strip()
                text = obj.get("text", "").strip()

                if not label or not text:
                    continue

                if label not in existing_labels:
                    node = {
                        "id": label,
                        "title": label,
                        "summary": text[:200] + "..." if len(text) > 200 else text
                    }
                    nodes.append(node)
                    new_nodes.append(node)
                    existing_labels.add(label)

            except Exception as e:
                print(f"[✗] Failed to parse line: {e}")

    # Link only newly added nodes linearly
    for i in range(1, len(new_nodes)):
        links.append({
            "source": new_nodes[i - 1]["id"],
            "target": new_nodes[i]["id"]
        })

    # Save updated graph
    graph = {
        "nodes": nodes,
        "links": links
    }
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"[✓] Saved graph with {len(nodes)} nodes and {len(links)} links → {graph_path}")
