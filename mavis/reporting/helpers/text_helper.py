def humanize(text: str) -> str:
    if not text:
        return text
    return text.replace("_", " ").capitalize()
