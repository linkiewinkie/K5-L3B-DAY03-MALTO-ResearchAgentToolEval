from __future__ import annotations

from typing import Any

from tools._shared import err, parse_date

VALID_BY = ("score", "date", "title")
VALID_ORDER = ("desc", "asc")


def _sort_value(item: dict[str, Any], by: str) -> float | str | None:
    """Return the value to sort on, or None when the item has nothing usable for `by`."""
    if by == "score":
        value = item.get("score")
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None
    if by == "date":
        parsed = parse_date(item.get("date"))
        return parsed.timestamp() if parsed else None
    title = item.get("title")
    return title.strip().casefold() if isinstance(title, str) and title.strip() else None


def rank_items(items: list[dict[str, Any]] | None = None, by: str = "score", order: str = "desc", limit: int = 0) -> dict[str, Any]:
    try:
        if by not in VALID_BY:
            raise ValueError(f"by must be one of {VALID_BY}, got {by!r}")
        if order not in VALID_ORDER:
            raise ValueError(f"order must be one of {VALID_ORDER}, got {order!r}")
        if items is None:
            items = []
        if not isinstance(items, list):
            raise TypeError(f"items must be a list, got {type(items).__name__}")
        limit = int(limit or 0)
        if limit < 0:
            raise ValueError(f"limit must be >= 0, got {limit}")

        ranked: list[tuple[Any, dict[str, Any]]] = []
        unranked: list[dict[str, Any]] = []
        skipped = 0
        for item in items:
            if not isinstance(item, dict):
                skipped += 1  # junk from the model: drop it, do not crash
                continue
            value = _sort_value(item, by)
            if value is None:
                unranked.append(item)  # keep, but always after the ranked ones
            else:
                ranked.append((value, item))

        ranked.sort(key=lambda pair: pair[0], reverse=(order == "desc"))
        result = [item for _, item in ranked] + unranked
        if limit > 0:
            result = result[:limit]
        return {
            "tool": "rank_items", "by": by, "order": order, "items": result,
            "input_count": len(items), "item_count": len(result),
            "unranked": len(unranked), "skipped": skipped,
        }
    except Exception as exc:
        return err("rank_items", exc)
