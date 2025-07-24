def truncate_text(text, max_chars=3000):
    if not text:
        return ""
    return text[:max_chars]
