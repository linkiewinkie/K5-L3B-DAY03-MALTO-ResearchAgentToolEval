from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from tools._shared import domain, err, parse_date


def _label(value: str) -> str:
    return value.strip().lower().lstrip("@").removeprefix("www.")


def _item_labels(item: dict[str, Any]) -> set[str]:
    """Names an item can be matched by: its `source` field and the domain of its url."""
    labels: set[str] = set()
    source = item.get("source")
    if isinstance(source, str) and source.strip():
        labels.add(_label(source))
    url = item.get("url")
    if isinstance(url, str) and url.strip():
        host = domain(url)
        if host:
            labels.add(_label(host))
    return labels


def _matches(wanted: str, labels: set[str]) -> bool:
    # "reuters" matches source "Reuters" and domain "reuters.com"; "reuters.com" matches exactly.
    return any(wanted == label or wanted in label.split(".") for label in labels)


def _as_sources(sources: Any) -> list[str]:
    if sources is None:
        return []
    if isinstance(sources, str):
        sources = sources.split(",")
    if not isinstance(sources, list):
        raise TypeError(f"sources must be a list of strings, got {type(sources).__name__}")
    wanted: list[str] = []
    for entry in sources:
        if not isinstance(entry, str):
            raise TypeError(f"sources must contain only strings, got {type(entry).__name__}")
        if entry.strip():
            wanted.append(_label(entry))
    return wanted


def filter_items(items: list[dict[str, Any]] | None = None, sources: list[str] | None = None, days: int = 0) -> dict[str, Any]:
    try:
        if items is None:
            items = []
        if not isinstance(items, list):
            raise TypeError(f"items must be a list, got {type(items).__name__}")
        wanted = _as_sources(sources)
        days = int(days or 0)
        if days < 0:
            raise ValueError(f"days must be >= 0, got {days}")
        cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days > 0 else None

        kept: list[dict[str, Any]] = []
        removed_by_source = removed_by_date = removed_undated = skipped = 0
        for item in items:
            if not isinstance(item, dict):
                skipped += 1
                continue
            if wanted and not any(_matches(name, _item_labels(item)) for name in wanted):
                removed_by_source += 1
                continue
            if cutoff is not None:
                parsed = parse_date(item.get("date"))
                if parsed is None:
                    removed_undated += 1  # cannot prove it is recent, so it is not kept
                    continue
                if parsed < cutoff:
                    removed_by_date += 1
                    continue
            kept.append(item)

        return {
            "tool": "filter_items", "sources": wanted, "days": days, "items": kept,
            "input_count": len(items), "item_count": len(kept),
            "removed_by_source": removed_by_source, "removed_by_date": removed_by_date,
            "removed_undated": removed_undated, "skipped": skipped,
        }
    except Exception as exc:
        return err("filter_items", exc)
