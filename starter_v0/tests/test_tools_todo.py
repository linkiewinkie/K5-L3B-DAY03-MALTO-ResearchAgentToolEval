"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

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


# ---------------- rank ----------------

rank_tool = TOOL_FUNCTIONS["rank"]


# 1. happy path
def test_rank_by_score_desc_keeps_top_n() -> None:
    items = [
        {"title": "low", "score": 0.2},
        {"title": "high", "score": 0.9},
        {"title": "mid", "score": 0.5},
    ]
    result = rank_tool(items=items, by="score", limit=2)

    assert [i["title"] for i in result["items"]] == ["high", "mid"]
    assert result["input_count"] == 3
    assert result["item_count"] == 2


def test_rank_by_date_handles_tweet_and_iso_formats_newest_first() -> None:
    items = [
        {"title": "tweet", "date": "Thu Nov 05 22:34:04 +0000 2026"},
        {"title": "iso", "date": "2026-11-08"},
        {"title": "newest", "date": "Tue Nov 10 10:21:49 +0000 2026"},
    ]
    result = rank_tool(items=items, by="date")
    assert [i["title"] for i in result["items"]] == ["newest", "iso", "tweet"]


def test_rank_by_title_ascending_ignores_case() -> None:
    items = [{"title": "banana"}, {"title": "Apple"}, {"title": "cherry"}]
    result = rank_tool(items=items, by="title", order="asc")
    assert [i["title"] for i in result["items"]] == ["Apple", "banana", "cherry"]


# 2. input xấu từ model
def test_rank_items_without_sort_field_go_last_even_in_ascending_order() -> None:
    items = [{"title": "no score"}, {"title": "b", "score": 2}, {"title": "a", "score": 1}, {"title": "bad", "score": "n/a"}]
    result = rank_tool(items=items, by="score", order="asc")

    assert [i["title"] for i in result["items"]] == ["a", "b", "no score", "bad"]
    assert result["unranked"] == 2


def test_rank_drops_non_dict_items_and_accepts_limit_as_string() -> None:
    items = ["junk", {"title": "x", "score": 1}, {"title": "y", "score": 2}, 42]
    result = rank_tool(items=items, limit="1")

    assert result["skipped"] == 2
    assert [i["title"] for i in result["items"]] == ["y"]


def test_rank_none_items_returns_empty_result() -> None:
    result = rank_tool(items=None)
    assert result["item_count"] == 0
    assert "error" not in result


# 3. nhánh lỗi: trả error dict, không raise
def test_rank_invalid_by_returns_error_dict() -> None:
    result = rank_tool(items=[{"score": 1}], by="popularity")
    assert result["error"] == "ValueError"
    assert "by must be one of" in result["message"]


def test_rank_invalid_order_and_negative_limit_return_error_dict() -> None:
    assert rank_tool(items=[], order="sideways")["error"] == "ValueError"
    assert rank_tool(items=[], limit=-1)["error"] == "ValueError"


def test_rank_non_list_items_returns_error_dict() -> None:
    assert rank_tool(items="not a list")["error"] == "TypeError"


# ---------------- extract_links ----------------

extract_links_tool = TOOL_FUNCTIONS["extract_links"]


# 1. happy path
def test_extract_links_returns_links_in_order_with_count() -> None:
    text = "Xem https://example.com/a và http://news.org/b/c?x=1 nhé."
    result = extract_links_tool(text=text)

    assert result["links"] == ["https://example.com/a", "http://news.org/b/c?x=1"]
    assert result["count"] == 2


def test_extract_links_strips_trailing_punctuation_and_markdown_parenthesis() -> None:
    text = "Đọc (https://example.com/a), rồi [bài này](https://example.com/b)! Cuối: https://example.com/c."
    result = extract_links_tool(text=text)
    assert result["links"] == ["https://example.com/a", "https://example.com/b", "https://example.com/c"]


def test_extract_links_keeps_balanced_parenthesis_inside_url() -> None:
    text = "Wiki: https://en.wikipedia.org/wiki/Python_(programming_language)"
    assert extract_links_tool(text=text)["links"] == ["https://en.wikipedia.org/wiki/Python_(programming_language)"]


# 2. input xấu từ model
def test_extract_links_removes_duplicates_by_default_and_can_keep_them() -> None:
    text = "https://a.com/x và lại https://a.com/x"
    default = extract_links_tool(text=text)
    keep_all = extract_links_tool(text=text, unique=False)

    assert default["count"] == 1 and default["total_found"] == 2
    assert keep_all["count"] == 2


def test_extract_links_empty_none_and_no_link_text_return_zero_without_error() -> None:
    for text in ("", None, "chỉ có chữ, không có link, ftp://x.com cũng không tính"):
        result = extract_links_tool(text=text)
        assert result["count"] == 0
        assert "error" not in result


def test_extract_links_treats_string_false_as_false_for_unique() -> None:
    text = "https://a.com/x https://a.com/x"
    assert extract_links_tool(text=text, unique="false")["count"] == 2


# 3. nhánh lỗi: trả error dict, không raise
def test_extract_links_non_string_text_returns_error_dict() -> None:
    result = extract_links_tool(text=["https://a.com"])
    assert result["error"] == "TypeError"
    assert "text must be a string" in result["message"]


# ---------------- summarize_stats ----------------

summarize_stats_tool = TOOL_FUNCTIONS["summarize_stats"]


# 1. happy path
def test_summarize_stats_counts_items_per_source_sorted_by_count() -> None:
    items = [
        {"source": "bbc.com"}, {"source": "dw.com"}, {"source": "bbc.com"},
        {"source": "bbc.com"}, {"source": "dw.com"}, {"source": "cnn.com"},
    ]
    result = summarize_stats_tool(items=items)

    assert result["total_items"] == 6
    assert result["source_count"] == 3
    assert result["sources"] == [
        {"source": "bbc.com", "count": 3},
        {"source": "dw.com", "count": 2},
        {"source": "cnn.com", "count": 1},
    ]


def test_summarize_stats_reports_oldest_newest_and_span_days() -> None:
    items = [
        {"source": "a", "date": "2026-11-10"},
        {"source": "a", "date": "Sun Nov 01 08:00:00 +0000 2026"},
        {"source": "a", "date": "2026-11-05T12:00:00Z"},
    ]
    result = summarize_stats_tool(items=items)

    assert result["oldest"].startswith("2026-11-01T08:00:00")
    assert result["newest"].startswith("2026-11-10T00:00:00")
    assert result["span_days"] == 8.67


# 2. input xấu từ model
def test_summarize_stats_handles_missing_source_missing_date_and_junk() -> None:
    items = [
        {"url": "https://www.example.com/x"},
        {"title": "no source no url", "date": "not a date"},
        "junk",
        {"source": "  ", "date": "2026-11-02"},
    ]
    result = summarize_stats_tool(items=items)

    assert result["total_items"] == 3
    assert result["skipped"] == 1
    assert result["undated"] == 2
    assert {s["source"]: s["count"] for s in result["sources"]} == {"example.com": 1, "unknown": 2}


def test_summarize_stats_top_sources_truncates_list_but_keeps_source_count() -> None:
    items = [{"source": "a"}, {"source": "a"}, {"source": "b"}, {"source": "c"}]
    result = summarize_stats_tool(items=items, top_sources="1")

    assert result["sources"] == [{"source": "a", "count": 2}]
    assert result["source_count"] == 3


def test_summarize_stats_empty_items_returns_zero_totals_and_no_dates() -> None:
    result = summarize_stats_tool(items=[])
    assert result["total_items"] == 0
    assert result["oldest"] is None and result["newest"] is None and result["span_days"] is None
    assert "error" not in result


# 3. nhánh lỗi: trả error dict, không raise
def test_summarize_stats_non_list_items_returns_error_dict() -> None:
    assert summarize_stats_tool(items="abc")["error"] == "TypeError"


def test_summarize_stats_negative_top_sources_returns_error_dict() -> None:
    result = summarize_stats_tool(items=[], top_sources=-2)
    assert result["error"] == "ValueError"
    assert "top_sources must be >= 0" in result["message"]

