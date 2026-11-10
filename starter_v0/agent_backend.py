"""Backend adapter: one stable Python API for any UI (Streamlit, web, bot) to talk to the agent.

It wraps the exact same tool loop as `chat.py` (`run_model_tool_loop`), so UI turns
behave identically to CLI turns and are logged in the same transcript format.

Usage:
    from agent_backend import AgentConfig, AgentSession

    session = AgentSession(AgentConfig(provider="openrouter", version="v3"))
    turn = session.send("Tweet mới nhất của Sam Altman là gì?")
    turn.status          # "answered" | "waiting_for_user" | "needs_confirmation" | "max_tool_rounds" | "provider_error"
    turn.assistant_text  # text to show the user
    turn.tool_calls      # flat list of ToolCallView (tool, args, result, ok, error, round)
    session.transcript_path  # transcripts/<version>_<provider>_<source>_<ts>.transcript.json

Clarify / confirmation are detected from tool output flags (`awaiting_user`,
`status == "needs_confirmation"`), not tool names, so renames don't break them.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]

# Turn statuses exposed to the UI.
ANSWERED = "answered"
WAITING_FOR_USER = "waiting_for_user"        # agent called the clarify tool -> show its question
NEEDS_CONFIRMATION = "needs_confirmation"    # a send tool was called without confirmed=true -> nothing was sent
MAX_TOOL_ROUNDS = "max_tool_rounds"
PROVIDER_ERROR = "provider_error"


@dataclass
class AgentConfig:
    provider: str = "openrouter"
    model: str | None = None                 # None -> provider default
    version: str = "v0"                      # label written into transcripts / artifact_version
    system_prompt_path: Path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path: Path = ARTIFACTS_DIR / "tools.yaml"
    history_window: int = 5                  # last N user/assistant pairs kept in context
    max_tool_rounds: int = 4
    transcripts_dir: Path = ROOT / "transcripts"
    source: str = "ui"                       # tag in transcript id/file name, e.g. "ui", "telegram"


@dataclass
class ToolCallView:
    """One executed tool call, flattened for display."""
    round: int
    tool: str
    args: dict[str, Any]
    result: Any
    ok: bool                                 # False when the tool returned an error dict
    error: str | None = None                 # "<error>: <message>" when ok is False


@dataclass
class TurnResult:
    turn_index: int
    user_text: str
    status: str
    assistant_text: str
    tool_calls: list[ToolCallView] = field(default_factory=list)
    error: str | None = None                 # set when status == provider_error
    started_at: str = ""
    ended_at: str = ""

    @property
    def awaiting_user(self) -> bool:
        return self.status == WAITING_FOR_USER

    @property
    def needs_confirmation(self) -> bool:
        return self.status == NEEDS_CONFIRMATION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _tool_error(result: Any) -> str | None:
    if isinstance(result, dict) and result.get("error"):
        return f"{result.get('error')}: {result.get('message', '')}".rstrip(": ")
    return None


def _flatten_tool_calls(rounds: list[dict[str, Any]]) -> list[ToolCallView]:
    views: list[ToolCallView] = []
    for rnd in rounds:
        for event in rnd.get("tool_results", []):
            result = event.get("result")
            error = _tool_error(result)
            views.append(ToolCallView(
                round=rnd.get("round", 0),
                tool=event.get("tool", ""),
                args=event.get("args", {}) or {},
                result=result,
                ok=error is None,
                error=error,
            ))
    return views


def _pending_confirmation(tool_calls: list[ToolCallView]) -> bool:
    """True if the last send-like call was refused for lack of confirmation.

    Detected by the tool's output flag (status == "needs_confirmation"), not by tool
    name, so it survives renames. A later successful send in the same turn clears it.
    """
    pending = False
    for call in tool_calls:
        if isinstance(call.result, dict):
            status = call.result.get("status")
            if status == "needs_confirmation":
                pending = True
            elif status == "sent":
                pending = False
    return pending


class AgentSession:
    """One conversation = one transcript file. Not thread-safe; keep one per user/browser session."""

    def __init__(self, config: AgentConfig | None = None, *, provider: Any | None = None) -> None:
        self.config = config or AgentConfig()
        if self.config.provider not in PROVIDERS and provider is None:
            raise ValueError(f"Unknown provider {self.config.provider!r}; choose one of {PROVIDERS}")

        # Prompt + tools are read once so every turn of a session uses the same hashes.
        self.system_prompt = Path(self.config.system_prompt_path).read_text(encoding="utf-8")
        self.tool_declarations = load_tool_declarations(Path(self.config.tools_path))
        self._openai_tools = to_openai_tools(self.tool_declarations)
        self.provider = provider or make_provider(self.config.provider)
        self.model_name = self.config.model or getattr(self.provider, "default_model", None)
        self.artifact_version = build_artifact_version(
            self.config.version, Path(self.config.system_prompt_path), Path(self.config.tools_path)
        )

        self.history: list[dict[str, str]] = []
        self.turns: list[TurnResult] = []

        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([
            safe_slug(self.config.version),
            safe_slug(self.config.provider),
            safe_slug(self.config.source),
            timestamp,
        ])
        self.transcript_path = Path(self.config.transcripts_dir) / f"{transcript_id}.transcript.json"
        self.transcript: dict[str, Any] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": self.config.provider,
            "model": self.model_name,
            "system_prompt": str(self.config.system_prompt_path),
            "tools": str(self.config.tools_path),
            "history_window": self.config.history_window,
            "max_tool_rounds": self.config.max_tool_rounds,
            "source": self.config.source,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }

    # ------------------------------------------------------------------ info
    @property
    def tool_names(self) -> list[str]:
        return [decl.get("name", "") for decl in self.tool_declarations]

    def info(self) -> dict[str, Any]:
        """Header data for the UI."""
        return {
            "provider": self.config.provider,
            "model": self.model_name,
            "version": self.config.version,
            "artifact_version": self.transcript.get("artifact_version"),
            "prompt_hash": self.transcript.get("prompt_hash"),
            "tools_hash": self.transcript.get("tools_hash"),
            "tools": self.tool_names,
            "transcript_path": str(self.transcript_path),
        }

    # ------------------------------------------------------------------ main API
    def send(self, user_text: str) -> TurnResult:
        """Run one user turn through the agent loop. Never raises for provider/tool errors."""
        user_text = (user_text or "").strip()
        if not user_text:
            raise ValueError("user_text is empty")

        turn_index = len(self.turns) + 1
        started_at = now_iso()
        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(self.history, self.config.history_window),
            {"role": "user", "content": user_text},
        ]
        record: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": started_at,
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        try:
            loop = run_model_tool_loop(
                provider=self.provider,
                messages=messages,
                tools=self._openai_tools,
                model=self.config.model,
                max_tool_rounds=self.config.max_tool_rounds,
            )
            record.update(loop)
            tool_calls = _flatten_tool_calls(loop["rounds"])
            status = loop["status"]
            if status == ANSWERED and _pending_confirmation(tool_calls):
                status = NEEDS_CONFIRMATION
            record["status"] = status
            assistant_text = loop["assistant_text"] or ""
            error = None
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:  # surface the error, never hide it
            error = f"{type(exc).__name__}: {exc}"
            record.update({"status": PROVIDER_ERROR, "error": error})
            status, assistant_text, tool_calls = PROVIDER_ERROR, "", []

        ended_at = now_iso()
        record["ended_at"] = ended_at
        self.transcript["turns"].append(record)
        write_transcript(self.transcript_path, self.transcript)

        turn = TurnResult(
            turn_index=turn_index,
            user_text=user_text,
            status=status,
            assistant_text=assistant_text,
            tool_calls=tool_calls,
            error=error,
            started_at=started_at,
            ended_at=ended_at,
        )
        self.turns.append(turn)
        return turn
