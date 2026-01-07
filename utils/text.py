import re

def format_bio_text(text):
    if not text:
        return text

    return re.sub(r'\.(?=\s*[A-ZŠĐČĆŽ])', '.\n', text).strip()
