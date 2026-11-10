"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

dedupe_tool = TOOL_FUNCTIONS["dedupe"]


# 1. happy path
def test_dedupe_removes_duplicate_urls_keeps_first_occurrence() -> None:
    items = [
        {"title": "A", "url": "https://example.com/a"},
        {"title": "B", "url": "https://example.com/b"},
        {"title": "A2", "url": "https://example.com/a"},
    ]
    result = dedupe_tool(items=items)

    assert result["item_count"] == 2
    assert result["input_count"] == 3
    assert [i["title"] for i in result["items"]] == ["A", "B"]


def test_dedupe_treats_www_trailing_slash_and_case_as_same_url() -> None:
    items = [{"url": "https://www.Example.com/a/"}, {"url": "https://example.com/a"}]
    assert dedupe_tool(items=items)["item_count"] == 1


# 2. input xấu từ model
def test_dedupe_skips_items_without_key_instead_of_crashing() -> None:
    items = [{"title": "no url"}, "not a dict", {"url": ""}, {"url": "https://example.com/x"}]
    result = dedupe_tool(items=items)

    assert result["item_count"] == 1
    assert result["skipped"] == 3


def test_dedupe_accepts_limit_given_as_string() -> None:
    items = [{"url": f"https://example.com/{i}"} for i in range(5)]
    assert dedupe_tool(items=items, limit="2")["item_count"] == 2


def test_dedupe_none_items_returns_empty_result() -> None:
    result = dedupe_tool(items=None)
    assert result["item_count"] == 0
    assert "error" not in result


# 3. nhánh lỗi: trả error dict, không raise
def test_dedupe_invalid_key_returns_error_dict() -> None:
    result = dedupe_tool(items=[{"url": "https://a.com"}], key="author")
    assert result["error"] == "ValueError"
    assert "key must be one of" in result["message"]


def test_dedupe_non_list_items_returns_error_dict() -> None:
    result = dedupe_tool(items="https://a.com")
    assert result["error"] == "TypeError"


# ---------------- filter_results ----------------

filter_tool = TOOL_FUNCTIONS["filter_results"]


def _days_ago(days: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


# 1. happy path
def test_filter_keeps_only_requested_sources_matching_name_or_domain_case_insensitive() -> None:
    items = [
        {"title": "r", "source": "Reuters"},
        {"title": "t", "url": "https://www.techcrunch.com/2026/11/ai"},
        {"title": "b", "source": "bbc.com"},
    ]
    result = filter_tool(items=items, sources=["reuters", "TechCrunch"])

    assert [i["title"] for i in result["items"]] == ["r", "t"]
    assert result["removed_by_source"] == 1


def test_filter_days_keeps_only_recent_items() -> None:
    items = [
        {"title": "recent", "date": _days_ago(2)},
        {"title": "old", "date": _days_ago(10)},
    ]
    result = filter_tool(items=items, days=7)

    assert [i["title"] for i in result["items"]] == ["recent"]
    assert result["removed_by_date"] == 1


def test_filter_combines_sources_and_days() -> None:
    items = [
        {"title": "ok", "source": "Reuters", "date": _days_ago(1)},
        {"title": "old reuters", "source": "Reuters", "date": _days_ago(30)},
        {"title": "recent other", "source": "CNN", "date": _days_ago(1)},
    ]
    result = filter_tool(items=items, sources=["Reuters", "TechCrunch"], days=7)

    assert [i["title"] for i in result["items"]] == ["ok"]
    assert (result["removed_by_source"], result["removed_by_date"]) == (1, 1)


# 2. input xấu từ model
def test_filter_drops_undated_items_only_when_days_is_set() -> None:
    items = [{"title": "no date"}, {"title": "bad date", "date": "yesterday-ish"}]

    assert filter_tool(items=items, days=7)["removed_undated"] == 2
    assert filter_tool(items=items, days=7)["item_count"] == 0
    assert filter_tool(items=items)["item_count"] == 2


def test_filter_accepts_sources_as_comma_separated_string() -> None:
    items = [{"source": "Reuters"}, {"source": "CNN"}, {"source": "TechCrunch"}]
    assert filter_tool(items=items, sources="Reuters, TechCrunch")["item_count"] == 2


def test_filter_without_criteria_returns_everything_and_skips_junk() -> None:
    result = filter_tool(items=[{"title": "a"}, "junk", 7, {"title": "b"}])
    assert result["item_count"] == 2
    assert result["skipped"] == 2
    assert filter_tool(items=None)["item_count"] == 0


# 3. nhánh lỗi: trả error dict, không raise
def test_filter_negative_days_returns_error_dict() -> None:
    result = filter_tool(items=[], days=-3)
    assert result["error"] == "ValueError"
    assert "days must be >= 0" in result["message"]


def test_filter_non_list_items_returns_error_dict() -> None:
    assert filter_tool(items="abc")["error"] == "TypeError"


def test_filter_sources_of_wrong_type_return_error_dict() -> None:
    assert filter_tool(items=[], sources=123)["error"] == "TypeError"
    assert filter_tool(items=[], sources=["Reuters", 5])["error"] == "TypeError"


# ---------------- topic_stats ----------------

topic_tool = TOOL_FUNCTIONS["topic_stats"]

ARTICLES = [
    {"title": "OpenAI launches new agent platform", "source": "reuters.com"},
    {"title": "OpenAI agent update said to boost coding", "source": "techcrunch.com"},
    {"title": "EU regulation of AI draws criticism", "source": "reuters.com"},
    {"title": "New regulation pushes OpenAI to disclose data", "source": "bbc.com"},
    {"title": "Gardening tips for spring", "source": "garden.org"},
]


# 1. happy path
def test_topic_stats_auto_ranks_topics_by_number_of_articles() -> None:
    result = topic_tool(items=ARTICLES)
    counts = {row["topic"]: row["article_count"] for row in result["topics"]}

    assert result["mode"] == "auto"
    assert result["total_articles"] == 5
    assert counts["openai"] == 3
    assert counts["regulation"] == 2
    assert result["topics"][0]["topic"] == "openai"


def test_topic_stats_reports_share_sources_and_example_title() -> None:
    row = next(r for r in topic_tool(items=ARTICLES)["topics"] if r["topic"] == "openai")

    assert row["share_pct"] == 60.0
    assert set(row["sources"]) == {"reuters.com", "techcrunch.com", "bbc.com"}
    assert row["example_title"] == "OpenAI launches new agent platform"


def test_topic_stats_custom_topics_use_whole_word_match_and_keep_zero_counts() -> None:
    items = ARTICLES + [{"title": "He said it was fine", "source": "x.com"}]
    result = topic_tool(items=items, topics=["AI", "agent", "blockchain"])
    counts = {row["topic"]: row["article_count"] for row in result["topics"]}

    assert result["mode"] == "custom"
    assert counts == {"ai": 1, "agent": 2, "blockchain": 0}  # "said" must not count as "ai"


# 2. input xấu từ model
def test_topic_stats_min_articles_and_top_n_limit_the_result() -> None:
    assert [r["topic"] for r in topic_tool(items=ARTICLES, top_n=1)["topics"]] == ["openai"]
    singles = topic_tool(items=ARTICLES, min_articles=1)["topics"]
    assert any(r["article_count"] == 1 for r in singles)


def test_topic_stats_empty_none_and_junk_items_do_not_crash() -> None:
    assert topic_tool(items=[])["topics"] == []
    assert topic_tool(items=None)["total_articles"] == 0
    result = topic_tool(items=["junk", {"title": "OpenAI OpenAI"}, {"title": "OpenAI again"}])
    assert result["skipped"] == 1
    assert result["topics"][0]["article_count"] == 2  # one vote per article, not per mention


def test_topic_stats_accepts_topics_as_comma_separated_string() -> None:
    result = topic_tool(items=ARTICLES, topics="OpenAI, regulation")
    assert {r["topic"] for r in result["topics"]} == {"openai", "regulation"}


# 3. nhánh lỗi: trả error dict, không raise
def test_topic_stats_invalid_numbers_return_error_dict() -> None:
    assert topic_tool(items=[], top_n=-1)["error"] == "ValueError"
    assert topic_tool(items=[], min_articles=-2)["error"] == "ValueError"


def test_topic_stats_wrong_types_return_error_dict() -> None:
    assert topic_tool(items="abc")["error"] == "TypeError"
    assert topic_tool(items=[], topics=99)["error"] == "TypeError"


# ---------------- reading_list ----------------

reading_list_tool = TOOL_FUNCTIONS["reading_list"]


@pytest.fixture
def list_file(tmp_path, monkeypatch):
    """Point the tool at a temp file so tests never touch the real reading_list.json."""
    path = tmp_path / "reading_list.json"
    monkeypatch.setenv("READING_LIST_PATH", str(path))
    return path


# 1. happy path
def test_reading_list_add_saves_entry_to_file_and_list_returns_it(list_file) -> None:
    saved = reading_list_tool(action="add", url="https://example.com/a", title="Bài A", note="đọc cuối tuần")

    assert saved["status"] == "saved"
    assert saved["entry"]["title"] == "Bài A"
    assert datetime.fromisoformat(saved["entry"]["saved_at"])
    assert json.loads(list_file.read_text(encoding="utf-8"))[0]["url"] == "https://example.com/a"

    listed = reading_list_tool(action="list")
    assert listed["count"] == 1
    assert listed["entries"][0]["note"] == "đọc cuối tuần"


def test_reading_list_remove_deletes_entry_and_reports_not_found(list_file) -> None:
    reading_list_tool(action="add", url="https://example.com/a")
    reading_list_tool(action="add", url="https://example.com/b")

    removed = reading_list_tool(action="remove", url="https://example.com/a")
    missing = reading_list_tool(action="remove", url="https://example.com/zzz")

    assert removed["status"] == "removed" and removed["count"] == 1
    assert missing["status"] == "not_found"
    assert [e["url"] for e in reading_list_tool(action="list")["entries"]] == ["https://example.com/b"]


# 2. input xấu từ model / guardrail
def test_reading_list_add_same_url_in_different_form_is_not_duplicated(list_file) -> None:
    reading_list_tool(action="add", url="https://example.com/a")
    again = reading_list_tool(action="add", url="https://www.Example.com/a/")

    assert again["status"] == "already_saved"
    assert reading_list_tool(action="list")["count"] == 1


def test_reading_list_clear_without_confirmation_keeps_everything(list_file) -> None:
    reading_list_tool(action="add", url="https://example.com/a")

    blocked = reading_list_tool(action="clear")
    assert blocked["status"] == "needs_confirmation"
    assert reading_list_tool(action="list")["count"] == 1

    done = reading_list_tool(action="clear", confirmed=True)
    assert done["status"] == "cleared" and done["removed"] == 1
    assert reading_list_tool(action="list")["count"] == 0


def test_reading_list_list_on_missing_file_returns_empty_without_error(list_file) -> None:
    result = reading_list_tool()
    assert result["count"] == 0
    assert "error" not in result
    assert not list_file.exists()  # listing must not create the file


# 3. nhánh lỗi: trả error dict, không raise
def test_reading_list_rejects_bad_url_and_does_not_write(list_file) -> None:
    for bad in ("", "not a url", "ftp://example.com/a"):
        result = reading_list_tool(action="add", url=bad)
        assert result["error"] == "ValueError"
    assert reading_list_tool(action="remove")["error"] == "ValueError"
    assert not list_file.exists()


def test_reading_list_unknown_action_returns_error_dict(list_file) -> None:
    result = reading_list_tool(action="archive")
    assert result["error"] == "ValueError"
    assert "action must be one of" in result["message"]


def test_reading_list_corrupted_file_returns_error_dict_and_is_not_overwritten(list_file) -> None:
    list_file.write_text("{not json", encoding="utf-8")

    result = reading_list_tool(action="add", url="https://example.com/a")

    assert result["error"] == "JSONDecodeError"
    assert list_file.read_text(encoding="utf-8") == "{not json"
