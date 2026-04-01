import re
from html import unescape

from app.models.ingest_models import ParsedDocument
from app.services.ingest.normalizer import normalize_text


HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return normalize_text(unescape(HTML_TAG_RE.sub(" ", text or "")))


def _parse_policy_entry(entry: dict) -> ParsedDocument | None:
    for field in ("embedding_text", "display_text", "raw_text", "text"):
        value = entry.get(field)
        if isinstance(value, str) and value.strip():
            raw_chunk_id = entry.get("chunk_id")
            chunk_id = str(raw_chunk_id).strip() if raw_chunk_id is not None else ""
            metadata = {
                "document_title": entry.get("document_title") or "Policy Document",
                "section_title": entry.get("section_title"),
                "source_type": "policy",
                "category": _first_list_item(entry.get("categories")),
                # Preserve source chunk ids so retrieval metrics can match labeled benchmarks.
                "chunk_id": chunk_id or None,
            }
            return ParsedDocument(text=normalize_text(value), metadata=metadata)
    return None


def _first_list_item(value: object) -> str | None:
    if not isinstance(value, list) or not value:
        return None
    first = value[0]
    if first is None:
        return None
    return str(first)


def _parse_qa_entry(entry: dict) -> ParsedDocument | None:
    title = normalize_text(str(entry.get("title", "")))
    body_raw = str(entry.get("body_text") or entry.get("body", ""))
    body = _strip_html(body_raw)

    answers = entry.get("answers", [])
    answer_blocks: list[str] = []
    if isinstance(answers, list):
        for answer in answers:
            if isinstance(answer, dict):
                answer_text = _strip_html(str(answer.get("body_text") or answer.get("body", "")))
                if answer_text:
                    answer_blocks.append(answer_text)
            elif isinstance(answer, str):
                cleaned = _strip_html(answer)
                if cleaned:
                    answer_blocks.append(cleaned)

    merged_text = "\n\n".join([part for part in [title, body, "\n\n".join(answer_blocks)] if part]).strip()
    if not merged_text:
        return None

    metadata = {
        "document_title": title or "StackOverflow QA",
        "section_title": None,
        "source_type": "qa",
        "category": "stackoverflow",
    }
    return ParsedDocument(text=merged_text, metadata=metadata)


def parse_records(records: list[dict]) -> list[ParsedDocument]:
    parsed: list[ParsedDocument] = []
    for entry in records:
        if not isinstance(entry, dict):
            continue

        if "document_title" in entry or "embedding_text" in entry:
            doc = _parse_policy_entry(entry)
        else:
            doc = _parse_qa_entry(entry)

        if doc is None or not doc.text:
            continue
        parsed.append(doc)

    return parsed
