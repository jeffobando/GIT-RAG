import re
import unicodedata
from collections import defaultdict


class Retriever:
    def __init__(self, embedder, vector_index, documents: list[dict]):
        self.embedder = embedder
        self.vector_index = vector_index
        self.documents = documents

    def _normalize(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))

    def _tokenize(self, text: str) -> set[str]:
        normalized = self._normalize(text).lower()
        tokens = re.findall(r"[a-zA-Z0-9_-]+", normalized)
        return {t for t in tokens if len(t) > 2}

    def _lexical_overlap(self, query_terms: set[str], text_terms: set[str]) -> float:
        if not query_terms:
            return 0.0
        if not text_terms:
            return 0.0
        return len(query_terms & text_terms) / len(query_terms)

    def _intent_terms(self, query_terms: set[str]) -> set[str]:
        intent_terms = set()

        branch_terms = {"rama", "ramas", "branch", "branches"}
        naming_terms = {"nombre", "nombres", "naming", "prefijo", "prefix", "convencion"}
        bug_terms = {"bug", "error", "errores", "fix", "fixes", "hotfix", "incidente"}

        if query_terms & branch_terms:
            intent_terms.update(
                {
                    "rama",
                    "ramas",
                    "branch",
                    "branches",
                    "feature",
                    "fix",
                    "bugfix",
                    "hotfix",
                    "chore",
                    "release",
                    "prefijo",
                    "nombre",
                    "descriptivos",
                }
            )
        if query_terms & naming_terms:
            intent_terms.update({"prefijo", "nombre", "descriptivos", "convencion"})
        if query_terms & bug_terms:
            intent_terms.update({"fix", "bugfix", "hotfix", "error", "incidente"})

        return intent_terms

    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        query = query.strip()
        if not query or not self.documents:
            return []

        # Retrieve a larger candidate pool, then re-rank for relevance/diversity.
        candidate_k = min(max(k * 12, 80), len(self.documents))

        query_vec = self.embedder.encode_query(query)
        scores, indices = self.vector_index.search(query_vec, candidate_k)
        query_terms = self._tokenize(query)
        intent_terms = self._intent_terms(query_terms)
        seen_idx = set()

        candidates: list[dict] = []
        for semantic_score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            seen_idx.add(int(idx))

            doc = self.documents[idx]
            text = doc["text"].strip()
            metadata = doc.get("metadata", {})
            text_terms = self._tokenize(text)
            section_blob = f"{metadata.get('section_title', '')} {metadata.get('document_title', '')}"
            section_terms = self._tokenize(section_blob)

            lexical_score = self._lexical_overlap(query_terms, text_terms)
            section_score = self._lexical_overlap(query_terms, section_terms)
            intent_score = self._lexical_overlap(intent_terms, text_terms) if intent_terms else 0.0
            policy_boost = 0.12 if metadata.get("source_type") == "policy" else 0.0
            combined_score = (
                float(semantic_score)
                + (0.35 * lexical_score)
                + (0.20 * section_score)
                + (0.25 * intent_score)
                + policy_boost
            )

            candidates.append(
                {
                    "semantic_score": float(semantic_score),
                    "combined_score": combined_score,
                    "text": text,
                    "metadata": metadata,
                }
            )

        # Lexical rescue pass for policy docs: if semantic retrieval misses the
        # exact branch-naming section, recover it using direct lexical intent matching.
        rescue_candidates: list[dict] = []
        for idx, doc in enumerate(self.documents):
            if idx in seen_idx:
                continue
            metadata = doc.get("metadata", {})
            if metadata.get("source_type") != "policy":
                continue

            text = doc["text"].strip()
            text_terms = self._tokenize(text)
            section_blob = f"{metadata.get('section_title', '')} {metadata.get('document_title', '')}"
            section_terms = self._tokenize(section_blob)

            lexical_score = self._lexical_overlap(query_terms, text_terms)
            section_score = self._lexical_overlap(query_terms, section_terms)
            intent_score = self._lexical_overlap(intent_terms, text_terms) if intent_terms else 0.0

            if lexical_score == 0.0 and section_score == 0.0 and intent_score == 0.0:
                continue

            rescue_score = (0.55 * lexical_score) + (0.25 * section_score) + (0.35 * intent_score) + 0.20
            rescue_candidates.append(
                {
                    "semantic_score": 0.0,
                    "combined_score": rescue_score,
                    "text": text,
                    "metadata": metadata,
                }
            )

        rescue_candidates.sort(key=lambda x: x["combined_score"], reverse=True)
        candidates.extend(rescue_candidates[: min(40, len(rescue_candidates))])
        candidates.sort(key=lambda x: x["combined_score"], reverse=True)

        seen_texts = set()
        per_doc_limit = defaultdict(int)
        results = []
        policy_target = min(k, max(2, (k * 3) // 5))
        current_policy = 0

        def can_add(item: dict) -> bool:
            text = item["text"]
            metadata = item["metadata"]
            doc_title = metadata.get("document_title") or "__unknown__"
            if text in seen_texts:
                return False
            if per_doc_limit[doc_title] >= 2:
                return False
            return True

        def add_item(item: dict) -> None:
            nonlocal current_policy
            text = item["text"]
            metadata = item["metadata"]
            doc_title = metadata.get("document_title") or "__unknown__"
            seen_texts.add(text)
            per_doc_limit[doc_title] += 1
            if metadata.get("source_type") == "policy":
                current_policy += 1
            results.append(
                {
                    "score": item["combined_score"],
                    "text": text,
                    "metadata": metadata,
                }
            )

        # First pass: prefer policy chunks to anchor corporate answers.
        for item in candidates:
            if current_policy >= policy_target:
                break
            if item["metadata"].get("source_type") != "policy":
                continue
            if not can_add(item):
                continue
            add_item(item)
            if len(results) >= k:
                return results

        # Second pass: fill remaining slots with best candidates.
        for item in candidates:
            if not can_add(item):
                continue
            add_item(item)
            if len(results) >= k:
                break

        return results
