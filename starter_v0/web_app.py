"""Web UI server for the Research Agent — calls the REAL agent (no mock).

Run from starter_v0/:
    python web_app.py                 # http://127.0.0.1:8000
    cloudflared tunnel --url http://localhost:8000   # public demo link

Only uses the Python standard library on top of the lab's own code:
- chat.run_model_tool_loop  : model <-> tool loop (same as chat.py)
- artifacts/versions/*      : prompt/tools snapshot of every version (v0..v3) + artifacts/ (current)
- transcripts/ui_*.json     : one transcript per web chat, same shape as chat.py

Env (optional):
    WEB_HOST=127.0.0.1  WEB_PORT=8000
    WEB_MAX_TURNS_PER_SESSION=15  WEB_MAX_TURNS_GLOBAL=300
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import threading
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# chat.py prints tool calls with emoji; keep that from crashing on a cp1252 console.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript  # noqa: E402  (also loads .env)
from providers import make_provider  # noqa: E402
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools  # noqa: E402

PROVIDER_NAME = "openrouter"
MODELS = [
    {"id": "openai/gpt-4o-mini", "label": "gpt-4o-mini", "note": "Mặc định · model dùng cho eval"},
    {"id": "z-ai/glm-5.3", "label": "glm-5.3", "note": "Thay thế"},
]
HOST = os.getenv("WEB_HOST", "127.0.0.1")
PORT = int(os.getenv("WEB_PORT", "8000"))
MAX_TURNS_PER_SESSION = int(os.getenv("WEB_MAX_TURNS_PER_SESSION", "15"))
MAX_TURNS_GLOBAL = int(os.getenv("WEB_MAX_TURNS_GLOBAL", "300"))
MAX_CHARS = 500
MAX_TOOL_ROUNDS = 6
HISTORY_WINDOW = 5
MAX_SESSIONS = 500
VERSIONS_FILE = ROOT / "artifacts" / "versions" / "versions.json"
INDEX_FILE = ROOT / "web" / "index.html"
TRANSCRIPTS_DIR = ROOT / "transcripts"


# --------------------------------------------------------------------------- versions
def crlf_hash(path: Path) -> str:
    """Runs were hashed on Windows checkouts (CRLF). Normalise so the check also works on LF checkouts."""
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(data).hexdigest()


def load_versions() -> tuple[dict[str, dict[str, Any]], str]:
    spec = json.loads(VERSIONS_FILE.read_text(encoding="utf-8"))
    versions: dict[str, dict[str, Any]] = {}
    for item in spec["versions"]:
        prompt_path = ROOT / item["system_prompt"]
        tools_path = ROOT / item["tools"]
        declarations = load_tool_declarations(tools_path)
        prompt_hash, tools_hash = crlf_hash(prompt_path), crlf_hash(tools_path)
        verified = None
        if item.get("prompt_hash"):
            verified = prompt_hash == item["prompt_hash"] and tools_hash == item["tools_hash"]
        versions[item["version"]] = {
            **item,
            "artifact_version": item.get("artifact_version") or f"{item['version']}+p{prompt_hash[:12]}+t{tools_hash[:12]}",
            "prompt_hash": prompt_hash,
            "tools_hash": tools_hash,
            "verified": verified,
            "system_prompt_text": prompt_path.read_text(encoding="utf-8"),
            "openai_tools": to_openai_tools(declarations),
            "tool_names": [d["name"] for d in declarations],
            "missing_impl": [d["name"] for d in declarations if d["name"] not in TOOL_FUNCTIONS],
        }
    default = spec.get("default") if spec.get("default") in versions else next(iter(versions))
    return versions, default


VERSIONS, DEFAULT_VERSION = load_versions()
PROVIDER = make_provider(PROVIDER_NAME)


# --------------------------------------------------------------------------- send gate
# The agent decides when to call `send`. The web UI adds one more guard: even with
# confirmed=true nothing is sent until the user clicks "Yes, send" in the page.
_ctx = threading.local()
_original_send = TOOL_FUNCTIONS["send"]


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)


def gated_send(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    session = getattr(_ctx, "session", None)
    if _truthy(confirmed) and session is not None:
        session.pending_send = str(text)
        return {
            "tool": "send_telegram",
            "status": "needs_ui_confirmation",
            "message": "Nothing was sent yet. The web UI shows a Confirm button; tell the user to press it to send.",
        }
    return _original_send(text=text, confirmed=False)


TOOL_FUNCTIONS["send"] = gated_send


# --------------------------------------------------------------------------- sessions
class Session:
    def __init__(self, version: str, model: str) -> None:
        self.id = uuid.uuid4().hex
        self.version = version
        self.model = model
        self.history: list[dict[str, str]] = []
        self.turns_used = 0
        self.pending_send: str | None = None
        self.lock = threading.Lock()
        ver = VERSIONS[version]
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        self.transcript_id = "_".join(["ui", safe_slug(version), PROVIDER_NAME, timestamp])
        self.transcript_path = TRANSCRIPTS_DIR / f"{self.transcript_id}.transcript.json"
        self.transcript: dict[str, Any] = {
            "transcript_id": self.transcript_id,
            "source": "web_ui",
            "version": version,
            "artifact_version": ver["artifact_version"],
            "prompt_hash": ver["prompt_hash"],
            "tools_hash": ver["tools_hash"],
            "provider": PROVIDER_NAME,
            "model": model,
            "system_prompt": ver["system_prompt"],
            "tools": ver["tools"],
            "history_window": HISTORY_WINDOW,
            "max_tool_rounds": MAX_TOOL_ROUNDS,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }

    def save(self) -> None:
        write_transcript(self.transcript_path, self.transcript)


SESSIONS: dict[str, Session] = {}
SESSIONS_LOCK = threading.Lock()
GLOBAL = {"turns": 0}
GLOBAL_LOCK = threading.Lock()


def create_session(version: str | None, model: str | None) -> Session:
    version = version if version in VERSIONS else DEFAULT_VERSION
    model = model if model in {m["id"] for m in MODELS} else MODELS[0]["id"]
    session = Session(version, model)
    with SESSIONS_LOCK:
        if len(SESSIONS) >= MAX_SESSIONS:
            SESSIONS.pop(next(iter(SESSIONS)))
        SESSIONS[session.id] = session
    return session


def compact(value: Any, *, max_str: int = 1500, max_list: int = 25) -> Any:
    """Trim big tool results before sending them to the browser (transcript keeps the full data)."""
    if isinstance(value, str):
        return value if len(value) <= max_str else value[:max_str] + "…"
    if isinstance(value, list):
        return [compact(v, max_str=max_str, max_list=max_list) for v in value[:max_list]]
    if isinstance(value, dict):
        return {k: compact(v, max_str=max_str, max_list=max_list) for k, v in value.items()}
    return value


def limits(session: Session) -> dict[str, int]:
    return {
        "turns_left": max(0, MAX_TURNS_PER_SESSION - session.turns_used),
        "max_turns": MAX_TURNS_PER_SESSION,
        "global_left": max(0, MAX_TURNS_GLOBAL - GLOBAL["turns"]),
    }


def chat_turn(session: Session, message: str) -> dict[str, Any]:
    with session.lock:
        if session.turns_used >= MAX_TURNS_PER_SESSION:
            return {"error": "session_limit", "message": "Hết lượt dùng thử cho cuộc chat này. Bấm New chat để bắt đầu lại.", **limits(session)}
        with GLOBAL_LOCK:
            if GLOBAL["turns"] >= MAX_TURNS_GLOBAL:
                return {"error": "global_limit", "message": "Demo đã dùng hết lượt cho hôm nay.", **limits(session)}
            GLOBAL["turns"] += 1
        session.turns_used += 1

        ver = VERSIONS[session.version]
        messages = [
            {"role": "system", "content": ver["system_prompt_text"]},
            *trim_history(session.history, HISTORY_WINDOW),
            {"role": "user", "content": message},
        ]
        turn: dict[str, Any] = {
            "turn_index": len(session.transcript["turns"]) + 1,
            "started_at": now_iso(),
            "user": message,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }
        session.pending_send = None
        _ctx.session = session
        try:
            result = run_model_tool_loop(
                provider=PROVIDER,
                messages=messages,
                tools=ver["openai_tools"],
                model=session.model,
                max_tool_rounds=MAX_TOOL_ROUNDS,
            )
            turn.update(result)
            session.history.append({"role": "user", "content": message})
            session.history.append({"role": "assistant", "content": result["assistant_text"]})
        except Exception as exc:  # provider/network errors are shown, not hidden
            turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
        finally:
            _ctx.session = None
        if session.pending_send is not None:
            turn["pending_send"] = session.pending_send
        turn["ended_at"] = now_iso()
        session.transcript["turns"].append(turn)
        session.save()

        return {
            "status": turn["status"],
            "assistant_text": turn.get("assistant_text") or "",
            "error": turn.get("error"),
            "rounds": compact(turn.get("rounds", [])),
            "pending_send": session.pending_send,
            **limits(session),
        }


def send_decision(session: Session, decision: str) -> dict[str, Any]:
    with session.lock:
        text = session.pending_send
        if text is None:
            return {"error": "nothing_pending", "message": "Không có nội dung nào đang chờ gửi."}
        session.pending_send = None
        if decision == "confirm":
            result = _original_send(text=text, confirmed=True)
            status = "ui_send_confirmed"
        else:
            result = {"tool": "send_telegram", "status": "cancelled_by_user"}
            status = "ui_send_cancelled"
        session.transcript["turns"].append({
            "turn_index": len(session.transcript["turns"]) + 1,
            "started_at": now_iso(),
            "user": f"[UI button] {'Yes, send' if decision == 'confirm' else 'Cancel'}",
            "status": status,
            "assistant_text": None,
            "rounds": [],
            "tool_events": [{"tool": "send", "args": {"text": text, "confirmed": decision == "confirm"}, "result": result}],
            "ended_at": now_iso(),
        })
        session.save()
        return {"status": status, "result": result}


def public_config() -> dict[str, Any]:
    return {
        "provider": PROVIDER_NAME,
        "models": MODELS,
        "default_version": DEFAULT_VERSION,
        "max_chars": MAX_CHARS,
        "versions": [
            {
                "version": v["version"],
                "label": v["label"],
                "commit": v.get("commit"),
                "artifact_version": v["artifact_version"],
                "verified": v["verified"],
                "metrics": v.get("metrics"),
                "run_file": v.get("run_file"),
                "eval_model": v.get("model"),
                "tools": v["tool_names"],
                "missing_impl": v["missing_impl"],
            }
            for v in VERSIONS.values()
        ],
    }


# --------------------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "ResearchAgentWeb/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter console
        sys.stderr.write(f"[web] {self.address_string()} {fmt % args}\n")

    def _json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length > 20_000:
            raise ValueError("request too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def _session(self, session_id: Any) -> Session | None:
        with SESSIONS_LOCK:
            return SESSIONS.get(str(session_id))

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            body = INDEX_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/api/config":
            self._json(public_config())
        elif url.path == "/api/transcript":
            session = self._session(parse_qs(url.query).get("session_id", [""])[0])
            if not session:
                self._json({"error": "unknown_session"}, 404)
            else:
                self._json(session.transcript)
        else:
            self._json({"error": "not_found"}, 404)

    def do_POST(self) -> None:
        try:
            data = self._body()
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": "bad_request", "message": str(exc)}, 400)
            return
        path = urlparse(self.path).path
        if path == "/api/session":
            session = create_session(data.get("version"), data.get("model"))
            self._json({"session_id": session.id, "version": session.version, "model": session.model,
                        "transcript_id": session.transcript_id, **limits(session)})
            return
        session = self._session(data.get("session_id"))
        if not session:
            self._json({"error": "unknown_session", "message": "Phiên đã hết hạn, bấm New chat."}, 404)
            return
        if path == "/api/chat":
            message = str(data.get("message", "")).strip()
            if not message:
                self._json({"error": "empty_message", "message": "Nhập câu hỏi trước nhé."}, 400)
            elif len(message) > MAX_CHARS:
                self._json({"error": "too_long", "message": f"Tối đa {MAX_CHARS} ký tự."}, 400)
            else:
                self._json(chat_turn(session, message))
        elif path == "/api/send":
            self._json(send_decision(session, "confirm" if data.get("decision") == "confirm" else "cancel"))
        else:
            self._json({"error": "not_found"}, 404)


def main() -> None:
    for v in VERSIONS.values():
        flag = {True: "hash khớp run", False: "HASH LỆCH run", None: "không có run"}[v["verified"]]
        missing = f" | thiếu code: {v['missing_impl']}" if v["missing_impl"] else ""
        print(f"  {v['version']:<8} {v['artifact_version']:<36} {flag}{missing}")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Research Agent web UI: http://{HOST}:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
