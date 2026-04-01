import json
from pathlib import Path


def discover_json_sources(raw_dir: Path) -> list[Path]:
    if not raw_dir.exists():
        return []
    return sorted(p for p in raw_dir.glob("*.json") if p.is_file())


def load_json_records(source_paths: list[Path]) -> list[dict]:
    dataset: list[dict] = []
    for file_path in source_paths:
        with file_path.open("r", encoding="utf-8-sig") as file_handle:
            loaded = json.load(file_handle)
        if isinstance(loaded, list):
            dataset.extend([entry for entry in loaded if isinstance(entry, dict)])
        elif isinstance(loaded, dict):
            dataset.append(loaded)
    return dataset
