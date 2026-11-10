"""Streamlit UI for the Research Agent.

Run from starter_v0/:
    streamlit run app.py
Expose publicly:
    cloudflared tunnel --url http://localhost:8501

All agent logic lives in agent_backend.py; this file only renders.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from agent_backend import (
    PROVIDERS,
    AgentConfig,
    AgentSession,
    TurnResult,
)
from chat import ARTIFACTS_DIR, ROOT

SAMPLE_QUESTIONS = [
    "Tweet mới nhất của Sam Altman là gì?",
    "Tóm tắt tin tức AI nổi bật tuần này",
    "Đọc giúp mình bài này",
    "Gửi bản tin vừa rồi lên Telegram",
]
CONFIRM_TEXT = "Tôi xác nhận, gửi đi."

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

# ---------------------------------------------------------------- sidebar config
with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model = st.text_input("Model (để trống = mặc định của provider)", value="") or None
    version = st.text_input("Version label", value="v0")
    system_prompt_path = Path(st.text_input("System prompt", value=str(ARTIFACTS_DIR / "system_prompt.md")))
    tools_path = Path(st.text_input("Tools", value=str(ARTIFACTS_DIR / "tools.yaml")))
    history_window = int(st.number_input("History window", min_value=0, max_value=20, value=5))
    max_tool_rounds = int(st.number_input("Max tool rounds", min_value=1, max_value=10, value=4))
    new_chat = st.button("🔄 Cuộc trò chuyện mới", use_container_width=True)

config = AgentConfig(
    provider=provider_name,
    model=model,
    version=version,
    system_prompt_path=system_prompt_path,
    tools_path=tools_path,
    history_window=history_window,
    max_tool_rounds=max_tool_rounds,
    source="ui",
)

# New session when config changes or user asks for a new chat.
if new_chat or st.session_state.get("config") != config:
    try:
        st.session_state.session = AgentSession(config)
        st.session_state.config = config
    except Exception as exc:  # show setup errors instead of hiding them
        st.session_state.pop("session", None)
        st.error(f"Không khởi tạo được agent: {type(exc).__name__}: {exc}")
        st.stop()

session: AgentSession = st.session_state.session
info = session.info()

with st.sidebar:
    st.divider()
    st.caption("Tools đang bật")
    st.code(", ".join(info["tools"]), language=None)

# ---------------------------------------------------------------- header
st.title("🔎 Research Agent")
st.caption(
    f"provider=`{info['provider']}` · model=`{info['model']}` · artifact_version=`{info['artifact_version']}`"
)


def render_turn(turn: TurnResult) -> None:
    with st.chat_message("user"):
        st.markdown(turn.user_text)
    with st.chat_message("assistant"):
        for call in turn.tool_calls:
            icon = "🔧" if call.ok else "❌"
            label = f"{icon} round {call.round} · `{call.tool}`({json.dumps(call.args, ensure_ascii=False)})"
            with st.expander(label, expanded=not call.ok):
                if not call.ok:
                    st.error(call.error)
                st.json(call.result, expanded=False)
        if turn.status == "provider_error":
            st.error(f"Provider error: {turn.error}")
            return
        if turn.awaiting_user:
            st.info("Agent đang hỏi lại (clarify) — trả lời ở ô chat bên dưới.")
        elif turn.needs_confirmation:
            st.warning("Agent cần bạn xác nhận trước khi gửi. Chưa có gì được gửi.")
        elif turn.status == "max_tool_rounds":
            st.warning("Dừng vì chạm giới hạn số vòng tool.")
        st.markdown(turn.assistant_text or "_(không có text)_")


for turn in session.turns:
    render_turn(turn)

pending: str | None = st.session_state.pop("pending", None)

if not session.turns:
    st.markdown("**Câu hỏi mẫu:**")
    cols = st.columns(len(SAMPLE_QUESTIONS))
    for col, question in zip(cols, SAMPLE_QUESTIONS):
        if col.button(question, use_container_width=True):
            st.session_state.pending = question
            st.rerun()
elif session.turns[-1].needs_confirmation:
    # Confirmation is an explicit user message, so the model still decides to call send(confirmed=true).
    if st.button(f"✅ {CONFIRM_TEXT}"):
        st.session_state.pending = CONFIRM_TEXT
        st.rerun()

user_text = st.chat_input("Hỏi agent...") or pending

if user_text:
    with st.spinner("Agent đang chạy..."):
        session.send(user_text)
    st.rerun()

if session.turns:
    st.caption(f"Transcript: `{Path(info['transcript_path']).relative_to(ROOT)}`")
