import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9.,;!?()\[\]\-\'\"\n ]', '', text)
    return text.strip()
