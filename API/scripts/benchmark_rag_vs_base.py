import argparse
import csv
import json
import re
import socket
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run benchmark queries against /evaluate (rag) and /evaluate/base (base).",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API base URL (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--questions",
        required=True,
        help=(
            "Path to questions file (.jsonl, .json, or .txt). "
            "Supported fields: question, reference_answer, relevant_chunk_ids."
        ),
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Top-k for rag evaluation (default: 5).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel workers (default: 4; local mode overrides to 1 unless explicitly set).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="HTTP timeout in seconds (default: 120; local mode overrides to 450 unless explicitly set).",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Retries per request on timeout/network errors (default: 2; local mode overrides to 1 unless explicitly set).",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="Base delay (seconds) between retries (default: 2.0).",
    )
    parser.add_argument(
        "--local-mode",
        action="store_true",
        help="Tune defaults for local LLM inference (workers=1, timeout=450, retries=1) unless explicitly provided.",
    )
    parser.add_argument(
        "--csv-out",
        default="",
        help="Optional CSV output path.",
    )
    return parser.parse_args()


def _request_json(
    method: str,
    url: str,
    timeout: float,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, method=method.upper(), data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        if not raw.strip():
            return {}
        return json.loads(raw)


def _request_json_with_retry(
    method: str,
    url: str,
    timeout: float,
    retries: int,
    retry_delay: float,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    last_exc: Exception | None = None
    attempts = max(1, retries + 1)
    for attempt in range(1, attempts + 1):
        try:
            return _request_json(method=method, url=url, timeout=timeout, payload=payload)
        except (socket.timeout, TimeoutError, urllib.error.URLError) as exc:
            last_exc = exc
            if attempt >= attempts:
                break
            time.sleep(retry_delay * attempt)
    if last_exc:
        raise last_exc
    raise RuntimeError("Unknown request failure.")


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    stripped = stripped.lower().strip()
    return re.sub(r"\s+", " ", stripped)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_-]+", _normalize_text(text))


def _exact_match(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 1.0 if _normalize_text(a) == _normalize_text(b) else 0.0


def _token_f1(prediction: str, reference: str) -> float:
    pred_tokens = _tokenize(prediction)
    ref_tokens = _tokenize(reference)
    if not pred_tokens or not ref_tokens:
        return 0.0
    pred_counts: dict[str, int] = {}
    ref_counts: dict[str, int] = {}
    for token in pred_tokens:
        pred_counts[token] = pred_counts.get(token, 0) + 1
    for token in ref_tokens:
        ref_counts[token] = ref_counts.get(token, 0) + 1

    overlap = 0
    for token, count in pred_counts.items():
        overlap += min(count, ref_counts.get(token, 0))

    if overlap == 0:
        return 0.0
    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def load_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Questions file not found: {path}")

    entries: list[dict[str, Any]] = []
    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        for line in lines:
            raw = line.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            if isinstance(obj, str):
                entries.append({"question": obj.strip()})
            elif isinstance(obj, dict):
                entries.append(obj)
    elif suffix == ".json":
        loaded = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(loaded, list):
            for obj in loaded:
                if isinstance(obj, str):
                    entries.append({"question": obj.strip()})
                elif isinstance(obj, dict):
                    entries.append(obj)
    else:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            q = line.strip()
            if q:
                entries.append({"question": q})

    normalized_entries: list[dict[str, Any]] = []
    for entry in entries:
        question = str(entry.get("question", "")).strip()
        if not question:
            continue
        reference_answer = str(entry.get("reference_answer", "")).strip()
        relevant_ids = entry.get("relevant_chunk_ids", [])
        if not isinstance(relevant_ids, list):
            relevant_ids = []
        relevant_ids = [str(item).strip() for item in relevant_ids if str(item).strip()]
        normalized_entries.append(
            {
                "question": question,
                "reference_answer": reference_answer,
                "relevant_chunk_ids": relevant_ids,
            }
        )
    return normalized_entries


def _mean_score(metrics: dict[str, Any]) -> float | None:
    values: list[float] = []
    for key in [
        "recall_at_k",
        "mrr",
        "hit_at_k",
        "ndcg_at_k",
        "faithfulness",
        "answer_relevance",
    ]:
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            values.append(float(value))
    if not values:
        return None
    return sum(values) / len(values)


def evaluate_pair(
    base_url: str,
    entry: dict[str, Any],
    k: int,
    timeout: float,
    retries: int,
    retry_delay: float,
) -> dict[str, Any]:
    question = entry["question"]
    reference_answer = entry.get("reference_answer", "")
    relevant_chunk_ids = entry.get("relevant_chunk_ids", [])

    rag_payload = {
        "query": question,
        "k": k,
        "run_type": "rag",
        "source_type": "rag",
        "relevant_chunk_ids": relevant_chunk_ids,
        "metadata": {"benchmark": "rag_vs_base"},
    }
    base_payload = {
        "query": question,
        "k": k,
        "run_type": "base",
        "source_type": "base",
        "relevant_chunk_ids": relevant_chunk_ids,
        "metadata": {"benchmark": "rag_vs_base"},
    }

    rag_url = f"{base_url.rstrip('/')}/evaluate"
    base_url_eval = f"{base_url.rstrip('/')}/evaluate/base"
    started = time.perf_counter()

    rag = _request_json_with_retry(
        "POST",
        rag_url,
        timeout,
        retries=retries,
        retry_delay=retry_delay,
        payload=rag_payload,
    )
    base = _request_json_with_retry(
        "POST",
        base_url_eval,
        timeout,
        retries=retries,
        retry_delay=retry_delay,
        payload=base_payload,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000

    rag_metrics = rag.get("metrics", {}) if isinstance(rag, dict) else {}
    base_metrics = base.get("metrics", {}) if isinstance(base, dict) else {}

    rag_answer = str(rag.get("answer", "")).strip()
    base_answer = str(base.get("answer", "")).strip()

    rag_ref_em = _exact_match(rag_answer, reference_answer) if reference_answer else None
    base_ref_em = _exact_match(base_answer, reference_answer) if reference_answer else None
    rag_ref_f1 = _token_f1(rag_answer, reference_answer) if reference_answer else None
    base_ref_f1 = _token_f1(base_answer, reference_answer) if reference_answer else None

    return {
        "question": question,
        "has_reference_answer": bool(reference_answer),
        "has_relevant_chunk_ids": bool(relevant_chunk_ids),
        "elapsed_ms": elapsed_ms,
        "rag_query_id": rag.get("query_id"),
        "base_query_id": base.get("query_id"),
        "rag_score": _mean_score(rag_metrics),
        "base_score": _mean_score(base_metrics),
        "rag_recall_at_k": rag_metrics.get("recall_at_k"),
        "base_recall_at_k": base_metrics.get("recall_at_k"),
        "rag_mrr": rag_metrics.get("mrr"),
        "base_mrr": base_metrics.get("mrr"),
        "rag_ndcg_at_k": rag_metrics.get("ndcg_at_k"),
        "base_ndcg_at_k": base_metrics.get("ndcg_at_k"),
        "rag_hit_at_k": rag_metrics.get("hit_at_k"),
        "base_hit_at_k": base_metrics.get("hit_at_k"),
        "rag_faithfulness": rag_metrics.get("faithfulness"),
        "base_faithfulness": base_metrics.get("faithfulness"),
        "rag_answer_relevance": rag_metrics.get("answer_relevance"),
        "base_answer_relevance": base_metrics.get("answer_relevance"),
        "rag_reference_em": rag_ref_em,
        "base_reference_em": base_ref_em,
        "rag_reference_f1": rag_ref_f1,
        "base_reference_f1": base_ref_f1,
    }


def _avg(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if isinstance(row.get(key), (int, float))]
    if not values:
        return None
    return sum(values) / len(values)


def print_summary(rows: list[dict[str, Any]], compare_payload: dict[str, Any] | None = None) -> None:
    print("\n=== Local Benchmark Summary ===")
    print(f"Samples: {len(rows)}")
    refs = sum(1 for row in rows if row.get("has_reference_answer"))
    labels = sum(1 for row in rows if row.get("has_relevant_chunk_ids"))
    print(f"With reference_answer: {refs}")
    print(f"With relevant_chunk_ids: {labels}")

    metrics_to_print = [
        ("rag_score", "RAG avg score"),
        ("base_score", "Base avg score"),
        ("rag_recall_at_k", "RAG Recall@k"),
        ("base_recall_at_k", "Base Recall@k"),
        ("rag_mrr", "RAG MRR"),
        ("base_mrr", "Base MRR"),
        ("rag_ndcg_at_k", "RAG nDCG@k"),
        ("base_ndcg_at_k", "Base nDCG@k"),
        ("rag_hit_at_k", "RAG Hit@k"),
        ("base_hit_at_k", "Base Hit@k"),
        ("rag_faithfulness", "RAG Faithfulness"),
        ("base_faithfulness", "Base Faithfulness"),
        ("rag_answer_relevance", "RAG Answer relevance"),
        ("base_answer_relevance", "Base Answer relevance"),
        ("rag_reference_f1", "RAG Reference F1"),
        ("base_reference_f1", "Base Reference F1"),
        ("rag_reference_em", "RAG Reference EM"),
        ("base_reference_em", "Base Reference EM"),
    ]
    for key, label in metrics_to_print:
        value = _avg(rows, key)
        print(f"{label}: {value:.4f}" if value is not None else f"{label}: -")

    rag_score = _avg(rows, "rag_score")
    base_score = _avg(rows, "base_score")
    if rag_score is not None and base_score is not None:
        print(f"Delta score (RAG - Base): {rag_score - base_score:+.4f}")

    rag_ref_f1 = _avg(rows, "rag_reference_f1")
    base_ref_f1 = _avg(rows, "base_reference_f1")
    if rag_ref_f1 is not None and base_ref_f1 is not None:
        print(f"Delta reference F1 (RAG - Base): {rag_ref_f1 - base_ref_f1:+.4f}")

    if compare_payload:
        left = compare_payload.get("left", {})
        right = compare_payload.get("right", {})
        print("\n=== Server Compare (/metrics/compare) ===")
        print(f"Left run_type: {left.get('run_type')} | samples: {left.get('samples')}")
        print(f"Right run_type: {right.get('run_type')} | samples: {right.get('samples')}")
        print(f"Avg score: {left.get('avg_score')} vs {right.get('avg_score')}")
        print(f"Avg nDCG@k: {left.get('avg_ndcg_at_k')} vs {right.get('avg_ndcg_at_k')}")
        print(f"Avg Hit@k: {left.get('avg_hit_at_k')} vs {right.get('avg_hit_at_k')}")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    argv = set(sys.argv[1:])

    if args.local_mode:
        if "--workers" not in argv:
            args.workers = 1
        if "--timeout" not in argv:
            args.timeout = 450.0
        if "--retries" not in argv:
            args.retries = 1

    entries = load_entries(Path(args.questions))
    if not entries:
        print("No questions found in input file.", file=sys.stderr)
        return 1

    print(f"Loaded {len(entries)} entries.")
    print(f"Running benchmark against {args.base_url} with {args.workers} workers...")

    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                evaluate_pair,
                args.base_url,
                entry,
                args.k,
                args.timeout,
                args.retries,
                args.retry_delay,
            ): entry["question"]
            for entry in entries
        }
        for future in as_completed(futures):
            question = futures[future]
            try:
                row = future.result()
                rows.append(row)
                print(f"OK: {question[:80]}")
            except urllib.error.HTTPError as exc:
                errors.append(f"HTTP {exc.code} for question: {question}")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"ERR for question '{question}': {exc}")

    compare_payload = None
    try:
        compare_url = f"{args.base_url.rstrip('/')}/metrics/compare?left_run_type=rag&right_run_type=base"
        compare_payload = _request_json("GET", compare_url, args.timeout)
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: failed to fetch /metrics/compare: {exc}")

    print_summary(rows, compare_payload=compare_payload)

    if args.csv_out:
        write_csv(Path(args.csv_out), rows)
        print(f"\nCSV written to: {args.csv_out}")

    if errors:
        print("\n=== Errors ===")
        for err in errors:
            print(err)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
