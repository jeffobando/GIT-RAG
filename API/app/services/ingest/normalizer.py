import re


try:
    import ftfy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    ftfy = None


def normalize_text(text: str) -> str:
    normalized = str(text or "")
    if ftfy is not None:
        normalized = ftfy.fix_text(normalized)

    normalized = (
        normalized.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\u00a0", " ")
        .replace("\u200b", "")
    )
    normalized = normalized.replace("â—", "-").replace("â—‹", "-")
    normalized = normalized.replace("ÃƒÂ¡", "á")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()
