import re


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def semantic_chunk_text(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    if not text.strip():
        return []

    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    if not sentences:
        return [text.strip()]

    chunks: list[str] = []
    current: list[str] = []

    for sentence in sentences:
        candidate = " ".join(current + [sentence]).strip()
        if len(candidate.split()) > max_tokens and current:
            chunks.append(" ".join(current).strip())
            current_words = " ".join(current).split()
            overlap = current_words[-overlap_tokens:] if overlap_tokens > 0 else []
            current = [" ".join(overlap), sentence] if overlap else [sentence]
        else:
            current.append(sentence)

    if current:
        chunks.append(" ".join(current).strip())

    return [chunk for chunk in chunks if chunk]
