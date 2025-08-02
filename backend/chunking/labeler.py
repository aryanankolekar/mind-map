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
PROMPT_TEMPLATE = """
Your task is to analyze the given text and generate a structured summary in a valid JSON format. The output must be a JSON array of objects, where each object represents a distinct topic from the text.

Each object in the JSON array must contain the following fields:
- "subject": The main subject category (e.g., "Computer Science").
- "topic": A specific topic within the subject (e.g., "Machine Learning").
- "subtopic": A finer-grained subtopic (e.g., "Deep Learning").
- "title": A concise, descriptive title for the text chunk.
- "summary": A detailed summary of the key points in the text chunk.

**Example of a valid JSON output:**
```json
[
  {
    "subject": "History",
    "topic": "World War II",
    "subtopic": "D-Day",
    "title": "The Normandy Landings",
    "summary": "The D-Day landings on June 6, 1944, marked the beginning of the end for Nazi Germany. Allied forces, including American, British, and Canadian troops, stormed the beaches of Normandy in the largest amphibious invasion in history. The operation, codenamed Overlord, was a pivotal moment in the war, opening a crucial second front in Western Europe."
  }
]
```

**Rules for the output:**
1.  The output must be a valid JSON array. Do not include any text or explanations outside of the JSON array.
2.  If the text covers multiple topics, create a separate object for each topic.
3.  If the text is short or covers a single topic, the output should be a JSON array with one object.
4.  Ensure all fields ("subject", "topic", "subtopic", "title", "summary") are present in each object.

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
            try:
                # Find the start of the JSON array
                json_start_index = generated_text.find('[')
                if json_start_index == -1:
                    raise ValueError("No JSON array found in the output.")

                # Find the end of the JSON array
                json_end_index = generated_text.rfind(']')
                if json_end_index == -1:
                    raise ValueError("JSON array is not properly closed.")

                # Extract the JSON string
                json_str = generated_text[json_start_index : json_end_index + 1]
                
                # Attempt to parse the JSON
                chunk_data = json.loads(json_str)

                if not chunk_data:
                    print(f"[WARNING] JSON output for chunk {i+1} is empty.")
                    continue

                if isinstance(chunk_data, list):
                    # Add the original text to each object
                    for item in chunk_data:
                        if isinstance(item, dict):
                            item['text'] = chunk
                    labeled_chunks.extend(chunk_data)
                    print(f"[SUCCESS] Chunk {i+1} processed successfully.")
                else:
                    print(f"[WARNING] JSON output for chunk {i+1} is not a list. Wrapping it in a list.")
                    if isinstance(chunk_data, dict):
                        chunk_data['text'] = chunk
                    labeled_chunks.extend([chunk_data])

            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to decode JSON for chunk {i+1}: {e}")
                print(f"       Raw JSON string: {json_str}")
            except ValueError as e:
                print(f"[ERROR] Failed to extract JSON for chunk {i+1}: {e}")
                print(f"       Generated text: {generated_text}")
            except Exception as e:
                print(f"[ERROR] An unexpected error occurred while processing chunk {i+1}: {e}")

        except Exception as e:
            print(f"[ERROR] Failed to process chunk {i+1} with the model: {e}")
            continue

    return labeled_chunks
