import json
import re
from pathlib import Path

from app.services.ingest.chunker import semantic_chunk_text


def _extract_pdf_pages(pdf_path: Path) -> list[str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except ModuleNotFoundError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PDF extraction requires pypdf or PyPDF2. Install one of them to use /ingest/upload-policy."
            ) from exc

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(re.sub(r"\s+", " ", text))
    if not pages:
        raise RuntimeError("No extractable text found in uploaded PDF.")
    return pages


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "uploaded-policy"


def generate_policy_json_from_pdf(pdf_path: Path, output_json_path: Path) -> int:
    pages = _extract_pdf_pages(pdf_path)
    full_text = "\n\n".join(pages).strip()
    if not full_text:
        raise RuntimeError("Uploaded PDF produced empty text after extraction.")

    chunks = semantic_chunk_text(text=full_text, max_tokens=140, overlap_tokens=20)
    if not chunks:
        chunks = [full_text]

    document_title = pdf_path.stem
    document_id = _slugify(document_title)
    records: list[dict] = []

    for idx, chunk in enumerate(chunks, start=1):
        chunk_id = f"{document_id}-{idx:03d}"
        records.append(
            {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_title": document_title,
                "document_type": "corporate_policy",
                "section_type": "uploaded_policy",
                "section_title": "Uploaded Policy",
                "source_sections": ["Uploaded Policy"],
                "policy_ids": [],
                "categories": [],
                "severities": [],
                "policy_metadata": [],
                "page_start": 1,
                "page_end": len(pages),
                "keywords": [],
                "token_estimate": len(chunk.split()),
                "raw_text": chunk,
                "display_text": chunk,
                "embedding_text": chunk,
            }
        )

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with output_json_path.open("w", encoding="utf-8") as file_handle:
        json.dump(records, file_handle, ensure_ascii=False, indent=2)
    return len(records)
