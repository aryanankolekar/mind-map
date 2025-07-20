import torch
from transformers import pipeline
import re
import json

# Initialize the model pipeline once
generator = None

def initialize_generator():
    global generator
    if generator is None:
        print("[INFO] Initializing the text generation model...")
        generator = pipeline("text-generation", model="databricks/dolly-v2-3b", device=0 if torch.cuda.is_available() else -1, trust_remote_code=True)
        print("[INFO] Model initialized.")

# Prompt for the LLM
PROMPT_TEMPLATE = """Below is a text about a variety of topics. Your task is to thoroughly analyze this text and generate a structured summary in a JSON-like format.

The output should be a list of objects, where each object represents a distinct topic found in the text. Each object must include the following fields:
- "subject": The main subject category (e.g., "Computer Science", "Physics", "History").
- "topic": A more specific topic within the subject (e.g., "Machine Learning", "Quantum Mechanics", "World War II").
- "subtopic": A finer-grained subtopic (e.g., "Deep Learning", "Quantum Entanglement", "D-Day").
- "title": A concise, descriptive title for the chunk of text.
- "summary": A detailed summary of the text chunk, capturing the key points and important details.

Rules for the output:
1. The output must be a valid JSON array of objects.
2. Do not include any text or explanations outside of the JSON array.
3. If the text covers multiple distinct topics, create a separate object for each.
4. If the text is short or covers only one topic, the output should be a list with a single object.
5. The "subject", "topic", and "subtopic" fields should be hierarchical and logical.

Now, analyze the following text and generate the structured summary:

{text}
"""

def chunk_text(text, max_chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i+max_chunk_size])
        if len(chunk.strip()) > 150:  # Skip very small fragments
            chunks.append(chunk)
    return chunks

def label_chunk(text):
    initialize_generator()
    
    chunks = chunk_text(text)
    labeled_chunks = []

    for i, chunk in enumerate(chunks):
        print(f"[INFO] Processing chunk {i+1}/{len(chunks)}...")
        prompt = PROMPT_TEMPLATE.format(text=chunk)
        
        try:
            raw_output = generator(prompt, max_new_tokens=500, num_return_sequences=1, eos_token_id=generator.tokenizer.eos_token_id)
            generated_text = raw_output[0]['generated_text']
            
            # Extract JSON part from the generated text
            json_match = re.search(r'\[.*\]', generated_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Basic cleaning
                json_str = json_str.replace("'", '"') # Replace single quotes
                
                try:
                    chunk_data = json.loads(json_str)
                    if isinstance(chunk_data, list):
                        # Add the original text to each object
                        for item in chunk_data:
                            if isinstance(item, dict):
                                item['text'] = chunk
                        labeled_chunks.extend(chunk_data)
                        print(f"[SUCCESS] Chunk {i+1} processed successfully.")
                    else:
                        print(f"[WARNING] JSON output for chunk {i+1} is not a list.")

                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to decode JSON for chunk {i+1}: {e}")
                    print(f"       Raw JSON string: {json_str}")
            else:
                print(f"[WARNING] No JSON output found for chunk {i+1}.")

        except Exception as e:
            print(f"[ERROR] Failed to process chunk {i+1} with the model: {e}")
            continue

    return labeled_chunks