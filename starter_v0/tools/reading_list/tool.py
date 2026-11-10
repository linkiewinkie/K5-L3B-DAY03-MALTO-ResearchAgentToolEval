from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from tools._shared import ROOT, err

VALID_ACTIONS = ("add", "list", "remove", "clear")


def _path() -> Path:
    """Where the list is stored. READING_LIST_PATH overrides it (tests use a temp file)."""
    custom = os.getenv("READING_LIST_PATH")
    return Path(custom).expanduser() if custom else ROOT / "reading_list.json"


def _norm_url(url: str) -> str:
    parsed = urlparse(url.strip())
    return f"{parsed.netloc.lower().removeprefix('www.')}{parsed.path.rstrip('/')}" + (f"?{parsed.query}" if parsed.query else "")


def _load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("reading list file is corrupted: expected a JSON list")
    return [entry for entry in data if isinstance(entry, dict)]


def _save(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _as_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "no")
    return bool(value)


def _require_url(url: Any) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url is required for this action")
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"url must start with http:// or https://, got {url!r}")
    return url


def manage_reading_list(action: str = "list", url: str = "", title: str = "", note: str = "", confirmed: bool = False) -> dict[str, Any]:
    try:
        if action not in VALID_ACTIONS:
            raise ValueError(f"action must be one of {VALID_ACTIONS}, got {action!r}")
        path = _path()
        entries = _load(path)

        if action == "list":
            return {"tool": "reading_list", "action": action, "entries": entries, "count": len(entries)}

        if action == "clear":
            if not _as_bool(confirmed):
                return {
                    "tool": "reading_list", "action": action, "status": "needs_confirmation", "count": len(entries),
                    "message": "Clearing deletes every saved article. Ask the user to confirm, then call again with confirmed=true.",
                }
            _save(path, [])
            return {"tool": "reading_list", "action": action, "status": "cleared", "removed": len(entries), "count": 0}

        url = _require_url(url)
        key = _norm_url(url)
        existing = next((e for e in entries if isinstance(e.get("url"), str) and _norm_url(e["url"]) == key), None)

        if action == "add":
            if existing is not None:
                return {"tool": "reading_list", "action": action, "status": "already_saved", "entry": existing, "count": len(entries)}
            entry = {
                "url": url,
                "title": title.strip() if isinstance(title, str) else "",
                "note": note.strip() if isinstance(note, str) else "",
                "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            entries.append(entry)
            _save(path, entries)
            return {"tool": "reading_list", "action": action, "status": "saved", "entry": entry, "count": len(entries)}

        # remove
        if existing is None:
            return {"tool": "reading_list", "action": action, "status": "not_found", "count": len(entries)}
        entries = [e for e in entries if e is not existing]
        _save(path, entries)
        return {"tool": "reading_list", "action": action, "status": "removed", "entry": existing, "count": len(entries)}
    except Exception as exc:
        return err("reading_list", exc)
