import re

def extract_sections(text):
    headers = ["Abstract", "Introduction", "Background", "Related Work", "Method", "Methodology",
               "Results", "Evaluation", "Discussion", "Conclusion", "References"]

    # Normalize and clean text
    clean = re.sub(r'\n+', '\n', text)
    clean = clean.replace('\r', '')
    section_map = {}

    # Build combined regex pattern
    pattern = '|'.join([fr"(?P<{h.lower().replace(' ', '_')}>{h})" for h in headers])
    regex = re.compile(fr"\b({pattern})\b", re.IGNORECASE)

    # Find all section headers
    matches = list(regex.finditer(clean))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(clean)
        section_name = match.group(1).strip().lower()
        section_map[section_name] = clean[start:end].strip()

    return section_map
