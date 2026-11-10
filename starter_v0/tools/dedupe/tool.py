from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from tools._shared import err

VALID_KEYS = ("url", "title")


def _norm_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{host}{path}" + (f"?{parsed.query}" if parsed.query else "")


def _norm_title(title: str) -> str:
    return " ".join(title.lower().split())


def dedupe_items(items: list[dict[str, Any]] | None = None, key: str = "url", limit: int = 0) -> dict[str, Any]:
    try:
        if key not in VALID_KEYS:
            raise ValueError(f"key must be one of {VALID_KEYS}, got {key!r}")
        if items is None:
            items = []
        if not isinstance(items, list):
            raise TypeError(f"items must be a list, got {type(items).__name__}")
        limit = int(limit or 0)

        seen: set[str] = set()
        kept: list[dict[str, Any]] = []
        skipped = 0
        for item in items:
            value = item.get(key) if isinstance(item, dict) else None
            if not isinstance(value, str) or not value.strip():
                skipped += 1  # item hỏng hoặc thiếu key: bỏ qua, không crash
                continue
            norm = _norm_url(value) if key == "url" else _norm_title(value)
            if norm in seen:
                continue
            seen.add(norm)
            kept.append(item)
            if limit > 0 and len(kept) >= limit:
                break
        return {
            "tool": "dedupe_items", "key": key, "items": kept,
            "input_count": len(items), "item_count": len(kept), "skipped": skipped,
        }
    except Exception as exc:
        return err("dedupe_items", exc)
