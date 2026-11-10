"""Offline tests for agent_backend.AgentSession (fake provider, no network, no API key)."""
from __future__ import annotations

import json
from typing import Any

import pytest

from agent_backend import (
    ANSWERED,
    NEEDS_CONFIRMATION,
    PROVIDER_ERROR,
    WAITING_FOR_USER,
    AgentConfig,
    AgentSession,
)
from providers.base import ModelResponse, ToolCall


class ScriptedProvider:
    """Returns pre-scripted responses in order and records every message list it received."""

    default_model = "fake-model"

    def __init__(self, responses: list[ModelResponse | Exception]) -> None:
        self.responses = list(responses)
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None) -> ModelResponse:
        self.calls.append(list(messages))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def make_session(tmp_path, responses: list[Any]) -> tuple[AgentSession, ScriptedProvider]:
    provider = ScriptedProvider(responses)
    session = AgentSession(
        AgentConfig(provider="openrouter", version="test", transcripts_dir=tmp_path, source="pytest"),
        provider=provider,
    )
    return session, provider


def test_plain_answer_is_returned_and_logged(tmp_path):
    session, _ = make_session(tmp_path, [ModelResponse(text="Xin chào")])

    turn = session.send("hi")

    assert turn.status == ANSWERED
    assert turn.assistant_text == "Xin chào"
    assert turn.tool_calls == []
    saved = json.loads(session.transcript_path.read_text(encoding="utf-8"))
    assert saved["source"] == "pytest"
    assert saved["turns"][0]["user"] == "hi"
    assert saved["turns"][0]["status"] == ANSWERED


def test_clarify_tool_pauses_turn_with_question(tmp_path):
    session, provider = make_session(tmp_path, [
        ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Bạn muốn xem tài khoản nào?"})]),
    ])

    turn = session.send("Xem tweet mới nhất")

    assert turn.status == WAITING_FOR_USER
    assert turn.awaiting_user
    assert turn.assistant_text == "Bạn muốn xem tài khoản nào?"
    assert [c.tool for c in turn.tool_calls] == ["clarify"]
    assert len(provider.calls) == 1  # loop stopped, did not call the model again


def test_send_without_confirmation_is_flagged_and_not_sent(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("send must not hit the network without confirmation")

    monkeypatch.setattr("requests.post", no_network)
    session, _ = make_session(tmp_path, [
        ModelResponse(tool_calls=[ToolCall("send", {"text": "digest", "confirmed": False})]),
        ModelResponse(text="Bạn xác nhận gửi không?"),
    ])

    turn = session.send("Gửi bản tin lên Telegram")

    assert turn.status == NEEDS_CONFIRMATION
    assert turn.needs_confirmation
    assert turn.tool_calls[0].result["status"] == "needs_confirmation"


def test_tool_error_is_surfaced_not_hidden(tmp_path):
    session, _ = make_session(tmp_path, [
        ModelResponse(tool_calls=[ToolCall("does_not_exist", {})]),
        ModelResponse(text="Xin lỗi, tool lỗi."),
    ])

    turn = session.send("làm gì đó")

    assert turn.status == ANSWERED
    assert turn.tool_calls[0].ok is False
    assert "unknown_tool" in turn.tool_calls[0].error


def test_provider_exception_becomes_provider_error_and_is_logged(tmp_path):
    session, _ = make_session(tmp_path, [RuntimeError("boom")])

    turn = session.send("hi")

    assert turn.status == PROVIDER_ERROR
    assert turn.error == "RuntimeError: boom"
    assert session.history == []  # failed turn is not added to model context
    saved = json.loads(session.transcript_path.read_text(encoding="utf-8"))
    assert saved["turns"][0]["status"] == PROVIDER_ERROR


def test_history_is_carried_into_next_turn(tmp_path):
    session, provider = make_session(tmp_path, [
        ModelResponse(text="Bạn muốn tài khoản nào?"),
        ModelResponse(text="OK sama"),
    ])

    session.send("Xem tweet mới nhất")
    session.send("sama")

    second_call = provider.calls[1]
    assert [m["content"] for m in second_call[1:]] == ["Xem tweet mới nhất", "Bạn muốn tài khoản nào?", "sama"]
    assert len(session.transcript["turns"]) == 2


def test_empty_message_is_rejected(tmp_path):
    session, _ = make_session(tmp_path, [])
    with pytest.raises(ValueError):
        session.send("   ")
