from app.models.ingest_models import ProcessedChunk


BAD_PATTERNS = (
    "|||||",
    ">>>>>>>",
    "=======",
    "rm -rf",
    "runner.os",
    "shell:",
)


def quality_score(text: str) -> int:
    score = 0
    lower = text.lower()
    words = text.split()

    if any(pattern in lower for pattern in BAD_PATTERNS):
        score -= 2
    if len(words) > 15:
        score += 1
    if len(words) < 350:
        score += 1
    if any(token in lower for token in ("git", "github", "branch", "rama", "fix/", "feature/", "pull request")):
        score += 1
    if "." in text:
        score += 1

    return score


def is_noisy(text: str, min_chunk_chars: int) -> bool:
    if len(text.strip()) < min_chunk_chars:
        return True
    return sum(pattern in text for pattern in BAD_PATTERNS) >= 2


def deduplicate_and_filter(
    chunk_candidates: list[ProcessedChunk],
    min_chunk_chars: int,
    min_quality_score_policy: int,
    min_quality_score_qa: int,
) -> list[ProcessedChunk]:
    seen: set[str] = set()
    filtered: list[ProcessedChunk] = []

    for item in chunk_candidates:
        text = item.text.strip()
        if not text:
            continue
        if text in seen:
            continue
        if is_noisy(text, min_chunk_chars):
            continue

        source_type = str(item.metadata.get("source_type", "qa"))
        min_quality = min_quality_score_policy if source_type == "policy" else min_quality_score_qa
        if quality_score(text) < min_quality:
            continue

        seen.add(text)
        filtered.append(ProcessedChunk(text=text, metadata=item.metadata))

    return filtered
