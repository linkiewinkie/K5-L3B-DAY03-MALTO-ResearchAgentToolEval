from __future__ import annotations

import re
from collections import Counter
from typing import Any

from tools._shared import domain, err, fold_text, terms

# Generic words that say nothing about a topic (accent-folded, lower-case).
EXTRA_STOPWORDS = {
    "about", "after", "also", "been", "before", "more", "most", "new", "news", "not", "now", "one",
    "over", "said", "says", "than", "that", "their", "there", "they", "this", "was", "were", "what",
    "when", "which", "while", "who", "will", "with", "would", "you", "your", "has", "have", "had",
    "its", "into", "out", "all", "can", "could", "may", "just", "year", "years", "week", "day",
    "today", "http", "https", "www", "com", "rt",
}


def _source_of(item: dict[str, Any]) -> str:
    source = item.get("source")
    if isinstance(source, str) and source.strip():
        return source.strip()
    url = item.get("url")
    return (domain(url) if isinstance(url, str) else "") or "unknown"


def _text_of(item: dict[str, Any]) -> str:
    return " ".join(str(item.get(key) or "") for key in ("title", "summary"))


def _auto_tokens(text: str) -> set[str]:
    return {t for t in terms(text) if len(t) >= 3 and not t.isdigit() and t not in EXTRA_STOPWORDS}


def _as_topics(topics: Any) -> list[str]:
    if topics is None:
        return []
    if isinstance(topics, str):
        topics = topics.split(",")
    if not isinstance(topics, list):
        raise TypeError(f"topics must be a list of strings, got {type(topics).__name__}")
    cleaned: list[str] = []
    for entry in topics:
        if not isinstance(entry, str):
            raise TypeError(f"topics must contain only strings, got {type(entry).__name__}")
        folded = fold_text(entry).strip()
        if folded and folded not in cleaned:
            cleaned.append(folded)
    return cleaned


def _row(topic: str, matches: list[dict[str, Any]], total: int) -> dict[str, Any]:
    sources = Counter(m["source"] for m in matches)
    top_sources = [name for name, _ in sorted(sources.items(), key=lambda kv: (-kv[1], kv[0]))[:3]]
    return {
        "topic": topic,
        "article_count": len(matches),
        "share_pct": round(len(matches) / total * 100, 1) if total else 0.0,
        "sources": top_sources,
        "example_title": next((m["title"] for m in matches if m["title"]), None),
    }


def analyze_topics(items: list[dict[str, Any]] | None = None, top_n: int = 10, min_articles: int = 2, topics: list[str] | None = None) -> dict[str, Any]:
    try:
        if items is None:
            items = []
        if not isinstance(items, list):
            raise TypeError(f"items must be a list, got {type(items).__name__}")
        top_n = int(top_n or 10)
        min_articles = int(min_articles or 2)
        if top_n < 1:
            raise ValueError(f"top_n must be >= 1, got {top_n}")
        if min_articles < 1:
            raise ValueError(f"min_articles must be >= 1, got {min_articles}")
        wanted = _as_topics(topics)

        docs: list[dict[str, Any]] = []
        skipped = 0
        for item in items:
            if not isinstance(item, dict):
                skipped += 1
                continue
            text = _text_of(item)
            title = item.get("title")
            docs.append({
                "folded": fold_text(text), "tokens": _auto_tokens(text),
                "source": _source_of(item), "title": title if isinstance(title, str) else "",
            })
        total = len(docs)

        rows: list[dict[str, Any]] = []
        if wanted:
            mode = "custom"
            for topic in wanted:
                pattern = re.compile(rf"(?<![a-z0-9]){re.escape(topic)}(?![a-z0-9])")
                rows.append(_row(topic, [d for d in docs if pattern.search(d["folded"])], total))
            rows.sort(key=lambda r: (-r["article_count"], r["topic"]))
        else:
            mode = "auto"
            counts: Counter[str] = Counter()
            for doc in docs:
                counts.update(doc["tokens"])  # tokens are a set: one vote per article
            ranked = sorted(((t, c) for t, c in counts.items() if c >= min_articles), key=lambda tc: (-tc[1], tc[0]))
            for topic, _ in ranked[:top_n]:
                rows.append(_row(topic, [d for d in docs if topic in d["tokens"]], total))

        return {"tool": "analyze_topics", "mode": mode, "total_articles": total, "topics": rows, "skipped": skipped}
    except Exception as exc:
        return err("analyze_topics", exc)
