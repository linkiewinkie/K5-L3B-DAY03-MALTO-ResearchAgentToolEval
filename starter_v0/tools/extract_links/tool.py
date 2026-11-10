from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from tools._shared import err

URL_RE = re.compile(r"https?://[^\s<>\"'\[\]]+", re.IGNORECASE)
TRAILING_PUNCT = ".,;:!?'\""


def _clean(url: str) -> str:
    """Strip sentence punctuation and an unbalanced closing ')' (e.g. from Markdown links)."""
    while url:
        if url[-1] in TRAILING_PUNCT:
            url = url[:-1]
        elif url.endswith(")") and url.count(")") > url.count("("):
            url = url[:-1]
        else:
            break
    return url


def _as_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "no")
    return bool(value)


def extract_links(text: str | None = "", unique: bool = True) -> dict[str, Any]:
    try:
        if text is None:
            text = ""
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, got {type(text).__name__}")

        found: list[str] = []
        for match in URL_RE.findall(text):
            url = _clean(match)
            if urlparse(url).netloc:
                found.append(url)

        links = list(dict.fromkeys(found)) if _as_bool(unique) else found
        return {"tool": "extract_links", "links": links, "count": len(links), "total_found": len(found)}
    except Exception as exc:
        return err("extract_links", exc)
