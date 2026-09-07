import re


def word_count(content: str) -> int:
    return len(re.findall(r"\S+", content))
