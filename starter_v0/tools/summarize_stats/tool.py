from __future__ import annotations

from collections import Counter
from typing import Any

from tools._shared import domain, err, parse_date


def _source_of(item: dict[str, Any]) -> str:
    source = item.get("source")
    if isinstance(source, str) and source.strip():
        return source.strip()
    url = item.get("url")
    return (domain(url) if isinstance(url, str) else "") or "unknown"


def summarize_stats(items: list[dict[str, Any]] | None = None, top_sources: int = 0) -> dict[str, Any]:
    try:
        if items is None:
            items = []
        if not isinstance(items, list):
            raise TypeError(f"items must be a list, got {type(items).__name__}")
        top_sources = int(top_sources or 0)
        if top_sources < 0:
            raise ValueError(f"top_sources must be >= 0, got {top_sources}")

        counts: Counter[str] = Counter()
        dates = []
        total = undated = skipped = 0
        for item in items:
            if not isinstance(item, dict):
                skipped += 1
                continue
            total += 1
            counts[_source_of(item)] += 1
            parsed = parse_date(item.get("date"))
            if parsed:
                dates.append(parsed)
            else:
                undated += 1

        sources = [{"source": name, "count": count} for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
        source_count = len(sources)
        if top_sources > 0:
            sources = sources[:top_sources]

        oldest = min(dates) if dates else None
        newest = max(dates) if dates else None
        return {
            "tool": "summarize_stats",
            "total_items": total,
            "source_count": source_count,
            "sources": sources,
            "oldest": oldest.isoformat() if oldest else None,
            "newest": newest.isoformat() if newest else None,
            "span_days": round((newest - oldest).total_seconds() / 86400, 2) if oldest and newest else None,
            "undated": undated,
            "skipped": skipped,
        }
    except Exception as exc:
        return err("summarize_stats", exc)
