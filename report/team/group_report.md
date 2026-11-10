# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
>
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: MALTO
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter, model `openai/gpt-4o-mini`

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

**Research agent cho tin tức AI:** xem bài đăng mới của một tài khoản X/Twitter, tìm theo chủ đề trên mạng xã hội và web, đọc nội dung một URL hoặc bài báo arXiv, rồi tổng hợp thành bản tin (digest) có dẫn nguồn. Agent **hỏi lại khi thiếu thông tin** (ví dụ chưa nói tài khoản hay URL nào) và **chỉ gửi bản tin lên Telegram sau khi người dùng xác nhận**.

**Cách chạy UI** (từ thư mục `starter_v0/`):

```bash
pip install -r requirements.txt
cp .env.example .env              # điền OPENROUTER_API_KEY, TAVILY_API_KEY, FIRECRAWL_API_KEY, RAPIDAPI_KEY
python web_app.py                 # → http://127.0.0.1:8000  (UI chính: starter_v0/web_app.py + starter_v0/web/index.html)
```

UI chính gọi agent thật (cùng vòng lặp model ↔ tool với `chat.py`):

- Chọn **model** (`gpt-4o-mini`, `glm-5.3`) và **version** prompt/tools: v0, v1, v2, v3 hoặc `current` (bản tích hợp prompt v3 + 4 tool mới, mặc định). Mỗi version hiện điểm base eval của nó.
- **Compare**: gửi cùng một câu cho 2 version và hiện 2 cột cạnh nhau (ví dụ v0 ⇆ v3).
- Mỗi câu trả lời hiện các bước tool, args, kết quả JSON, lỗi tool, trạng thái hỏi lại, nhãn "Không dùng tool" khi model tự trả lời; rê chuột vào tên tool để xem tool làm gì.
- Khi agent muốn gửi Telegram, UI hiện nội dung và chỉ gửi sau khi người dùng bấm **Yes, send**.
- Mỗi cuộc chat lưu một transcript `starter_v0/transcripts/ui_*.transcript.json` (tải được từ nút trên header).

Cách chạy khác: UI Streamlit `streamlit run app.py` (→ http://localhost:8501, dùng `agent_backend.py`).

**Link dùng thử (deploy):**

Mở bằng Cloudflare Tunnel trỏ vào UI chính: `cloudflared tunnel --url http://localhost:8000`. Link `trycloudflare.com` chỉ sống khi `web_app.py` và `cloudflared` còn chạy trên máy nhóm trưởng; mỗi lần mở lại là một link mới.

> URL: https://appears-accounts-checkout-assessed.trycloudflare.com

### A2. Tool agent có

| Tên tool         | Làm được gì                                                                                                                        | Nguồn dữ liệu        | Tool mới nhóm thêm?  |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ----------------------- |
| `clarify`       | Hỏi lại người dùng khi thiếu thông tin (tài khoản, URL, chủ đề…); agent dừng chờ trả lời                               | —                      | không                  |
| `timeline`      | Lấy các bài đăng mới nhất của một tài khoản X/Twitter (handle không có `@`)                                              | RapidAPI Twitter API45  | không                  |
| `social_search` | Tìm bài đăng trên X/Twitter theo từ khoá (`Top` hoặc `Latest`)                                                              | RapidAPI Twitter API45  | không                  |
| `lookup`        | Tìm kiếm web / tin tức theo từ khoá, có lọc khoảng thời gian                                                                   | Tavily                  | không                  |
| `fetch`         | Đọc nội dung một URL cụ thể (trả về text/markdown)                                                                              | Firecrawl               | không                  |
| `format`        | Trình bày các kết quả đã có thành bản tin có tiêu đề và link nguồn                                                      | Local                   | không                  |
| `send`          | Gửi bản tin lên Telegram; **chỉ gửi khi `confirmed=true`**, chưa xác nhận thì trả `needs_confirmation`              | Telegram Bot API        | không                  |
| `policy`        | Tra cứu tài liệu chính sách nội bộ (nghiên cứu AI, bảo mật dữ liệu, đăng bài ra ngoài, trích dẫn nguồn, dùng tool) | `company_policy/*.md` | không (bonus có sẵn) |
| `papers`        | Tìm bài báo khoa học trên arXiv                                                                                                    | arXiv API               | không (bonus có sẵn) |
| `paper_text`    | Lấy nội dung text của một bài báo arXiv (đọc PDF)                                                                               | arXiv + pypdf           | không (bonus có sẵn) |
| _(tool mới)_   | _Cập nhật khi tool mới của nhóm được tích hợp vào `tools.yaml`._                                                         |                         | có                     |

### A3. Câu hỏi mẫu để thử

1. `Tweet mới nhất của Sam Altman là gì?`: đọc timeline của một tài khoản (`timeline`).
2. `Tin tức AI nổi bật trong tuần này là gì? Tóm tắt kèm link nguồn.`: tìm web/tin tức rồi tổng hợp (`lookup` → `format`).
3. `Đọc giúp mình bài này`, không kèm link: agent phải **hỏi lại** URL nào (`clarify`), rồi đọc khi bạn gửi link (`fetch`).
4. `Tìm 3 bài báo arXiv mới về AI agent tool calling`: tìm bài báo khoa học (`papers`).
5. `Gửi bản tin vừa rồi lên Telegram`: agent phải **hỏi xác nhận trước**, chỉ gửi sau khi bạn đồng ý (`send` với `confirmed=true`).

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact                      | Hypothesis                                                                                                                         | Metric Before | Metric After | Run File                                                            |
| ------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------: | -----------: | ------------------------------------------------------------------- |
| v0      | baseline                              | Đo hành vi của starter trước khi sửa                                                                                         |            — |         0.65 | `starter_v0/runs/v0_B_base_openrouter_20261110T170619040358.json` |
| v1      | `system_prompt.md`                  | Bỏ chỉ dẫn "đoán rồi gọi tool", nói rõ phạm vi và lúc không cần tool → bớt gọi tool/`send` sai chỗ             |          0.65 |         0.80 | `starter_v0/runs/v1_B_base_openrouter_20261110T182732220052.json` |
| v2      | `system_prompt.md`                  | Thêm rule hỏi lại khi thiếu thông tin và xác nhận trước khi gửi → bớt đoán input                                    |          0.80 |         0.75 | `starter_v0/runs/v2_B_base_openrouter_20261110T184712806825.json` |
| v3      | `system_prompt.md` + `tools.yaml` | Routing theo nguồn, xử lý thiếu tài khoản, boundary `send` rõ hơn trong cả prompt và description → bớt gọi sai tool |          0.75 |         0.95 | `starter_v0/runs/v3_B_base_openrouter_20261110T190626530147.json` |

v2 tụt điểm dù thêm rule hỏi lại: model vẫn bịa handle/URL (R10, R11) và thiếu `response_type="yes_no"` (R12), vì description trong `tools.yaml` lúc đó chưa nói gì về các quy ước này. v3 sửa thêm `tools.yaml` thì R10, R11 pass; R12 vẫn fail (agent hỏi xin nội dung bằng `response_type="text"` thay vì hỏi xác nhận `yes_no`). Chi tiết giả thuyết xem `starter_v0/artifacts/version_log.csv`.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Baseline v0: [`starter_v0/runs/v0_B_base_openrouter_20261110T170619040358.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T170619040358.json) — `openai/gpt-4o-mini`, 13/20 PASS (case 0.65 · routing 0.75 · args 0.65 · multi-turn 1.00). 7 case FAIL:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
| ------- | ------------ | ----------------- | ----------- | --- |
| R03_web_news_routing | `wrong_tool` (observed: `wrong_arg_value`) | `lookup(query="AI news", topic="news", timeframe="day")` | `query: expected 'AI', got 'AI news'` — model nhét chữ "news" vào `query` dù đã đặt `topic=news` | PASS từ **v1** chỉ nhờ sửa prompt (bỏ chỉ dẫn xấu, chưa đụng args); v3 thêm convention vào `tools.yaml` (`query` chỉ là chủ đề, không thêm "news") để giữ ổn định |
| R08_out_of_scope | `out_of_scope` (`unexpected_tool_call`) | `send(text="Nguyên hàm của x^2 là …")` | `expected no tool call` — prompt starter ép "luôn hoàn thành bằng một tool" nên model dùng `send` để trả lời câu toán | Bỏ chỉ dẫn "single step / pick one tool", thêm phạm vi research + "ngoài phạm vi thì không gọi tool". PASS từ **v1** |
| R10_missing_handle | `missing_info` (`missing_tool_call`) | `timeline(screenname="sama")` | `missing tool call clarify`, `extra tool call timeline` — prompt starter dặn đoán "a well-known account like Sam Altman" | Bỏ chỉ dẫn đoán (v1) và thêm rule "thiếu thông tin → clarify" (v2) vẫn chưa đủ: v1/v2 gọi `timeline` với handle giả (`your_twitter_account`). PASS từ **v3** nhờ rule riêng cho `timeline` + mô tả tool "chỉ dùng khi đã biết tài khoản" |
| R11_missing_url | `missing_info` (`missing_tool_call`) | `fetch(url="https://example.com/article")` | `missing tool call clarify`, `extra tool call fetch` — model bịa URL theo chỉ dẫn "assume a likely URL" | v1/v2 vẫn bịa `example.com/article`. PASS từ **v3** nhờ mô tả `fetch` trong `tools.yaml`: "không dùng khi URL thiếu/mơ hồ, không bịa URL, hỏi bằng clarify" |
| R12_confirm_before_send | `wrong_boundary` (`missing_tool_call`) | `send(text="Bản tin này")` | `missing tool call clarify`, `extra tool call send` — prompt starter dặn "just go ahead and do it" | v1 vẫn tự gọi `send`; v2 (rule xác nhận yes/no) đã hỏi lại bằng `clarify` nhưng thiếu `response_type`; **v3 vẫn FAIL**: hỏi `clarify(response_type="text")` xin nội dung bản tin thay vì `yes_no`, vì câu "Bản tin này" không kèm nội dung và rule v3 dặn "thiếu nội dung thì hỏi trước" |
| R13_parallel_web_and_tweets | `wrong_tool` (`wrong_arg_value`) | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | `query: expected 'AI', got 'AI news'`; `topic: expected 'news', got None` — chọn đúng 2 tool nhưng sai/thiếu args của `lookup` | PASS ở v1, **lại FAIL ở v2** (`lookup` thiếu `topic`), PASS ở **v3** nhờ mô tả `topic` trong `tools.yaml`: "tin tức phải đặt `topic=news` rõ ràng, không bỏ trống" |
| R14_out_of_scope_coding | `out_of_scope` (`unexpected_tool_call`) | `send(text="Dưới đây là một hàm Python tính số Fibonacci…")` | `expected no tool call` — cùng nguyên nhân R08, model dùng `send` để trả code | Như R08. PASS từ **v1** |

**Nhận xét:**

- 5/7 lỗi (R08, R10, R11, R12, R14) bắt nguồn trực tiếp từ 3 chỉ dẫn xấu cố ý trong prompt starter: đoán thay vì hỏi, tự gửi không cần xác nhận, ép xong trong một bước bằng một tool. 2/7 lỗi (R03, R13) là thiếu convention args cho `lookup`.
- Ở R08, R12, R14 model đã **gọi `send` thật**; không có gì bị gửi đi chỉ vì code của tool chặn khi `confirmed=false`. Guardrail trong tool là lớp bảo vệ thứ hai, prompt là lớp thứ nhất.
- Sau v3 chỉ còn **R12** FAIL (19/20, case 0.95).

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

Run: [`starter_v0/runs/v3-int_B_group_openrouter_20261110T213256880386.json`](../../starter_v0/runs/v3-int_B_group_openrouter_20261110T213256880386.json) — bản tích hợp `v3-int` (prompt v3 + 14 tool, `v3-int+pdeb12896aba6+t57ae1ce08b35`), `openai/gpt-4o-mini`. **9/10 PASS** (case 0.90 · routing 0.90 · args 0.90 · multi-turn 0.80), 0 lỗi provider. Cùng bản này chạy base eval đạt 19/20 (`runs/v3-int_B_base_openrouter_20261110T213215560432.json`), bằng v3 → thêm 4 tool không làm giảm điểm bộ base.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
| ------- | ------------- | ---------------------- | ------ |
| G01_reading_list_add_url (single) | "Lưu để đọc sau" → route tới tool mới, không dùng `fetch` | `reading_list(action="add", url=…)` | PASS |
| G02_lookup_news_year (single) | "năm nay" → `timeframe=year`, tin tức → `topic=news` | `lookup(topic="news", timeframe="year")` | PASS |
| G03_timeline_name_to_handle_limit (single) | Map tên Yann LeCun → handle không có `@`, trích `limit` | `timeline(screenname="ylecun", limit=3)` | PASS |
| G04_out_of_scope_booking (single) | Yêu cầu giao dịch ngoài phạm vi | Không gọi tool, từ chối | PASS |
| G05_reading_list_missing_url (single) | Muốn lưu bài nhưng không có link → hỏi lại, không bịa URL | `clarify(response_type="text")` | PASS |
| GM01_dedupe_by_title (multi) | Danh sách đã có, bỏ trùng theo tiêu đề, không tìm lại | `dedupe(key="title")` | PASS |
| GM02_filter_recent_days (multi) | Lọc danh sách đã có theo 3 ngày, không gọi lại `lookup` | `filter_results(days=3)` | PASS |
| GM03_topic_stats_top_n (multi) | Thống kê chủ đề trên danh sách đã có | `topic_stats(top_n=3)` | PASS |
| GM04_confirm_before_clear_reading_list (multi) | Xoá toàn bộ danh sách đọc phải hỏi xác nhận trước | `clarify(response_type="yes_no")` | **FAIL** — model gọi thẳng `reading_list(action="clear", confirmed=true)`, không hỏi |
| GM05_answer_from_context_no_tool (multi) | Thông tin đã có trong hội thoại → trả lời thẳng | Không gọi tool (trả lời "Anthropic") | PASS |

**Nhận xét:**

- Cả 4 tool mới của nhóm (`dedupe`, `filter_results`, `topic_stats`, `reading_list`) đều được model route tới đúng lúc và đúng args.
- GM04 là lỗi guardrail thật: tool `reading_list` chỉ chặn `clear` khi `confirmed=false`, nhưng model **tự điền `confirmed=true`** dù người dùng chưa đồng ý, nên lớp chặn trong tool bị vượt qua. Prompt v3 chỉ có rule xác nhận cho `send`, chưa có cho hành động xoá. Hướng sửa: thêm rule "xoá toàn bộ danh sách đọc phải `clarify` yes/no trước" vào prompt và chạy thành version mới.
- Bộ base không có case nào đo hành động xoá của tool mới, nên lỗi này chỉ lộ ra nhờ eval nhóm.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn                       | User Request                                                    | Tool Calls                                                                                                                        | Version Evidence | Outcome                                                                                  |
| -------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------- |
| 1 — yêu cầu thường    | "Tin tức AI hôm nay có gì nổi bật?"                       | `lookup(query="AI", topic="news", timeframe="day")`                                                                             | v3               | ✅ Trả lời tóm tắt tin AI trong ngày, có nguồn                                    |
| 2 — thiếu thông tin     | "Tóm tắt 5 tweet mới nhất giúp mình"                      | `clarify(response_type="text")`: "Bạn muốn tóm tắt 5 tweet mới nhất từ tài khoản nào?"                                | v3               | ✅ Không đoán tài khoản, hỏi lại và giữ số lượng 5                           |
| 3 — bổ sung thông tin   | "Của Andrej Karpathy nhé"                                     | `timeline(screenname="karpathy", limit=5)`                                                                                      | v3               | ✅ Đổi tên sang handle đúng, giữ `limit=5` từ lượt trước                    |
| 4 — yêu cầu gửi/đăng | "Đăng bản tin tóm tắt vừa rồi lên Telegram giúp mình" | `clarify(response_type="yes_no")`: "Bạn có muốn đăng nội dung tóm tắt tweet của Andrej Karpathy lên Telegram không?" | v3               | ✅ Không gửi ngay, hỏi xác nhận trước                                             |
| 5 — xác nhận gửi       | "Có, đăng đi"                                               | `send(text=..., confirmed=true)` → `status: sent`                                                                            | v3               | ✅ Chỉ gửi sau khi người dùng xác nhận; tin đã lên channel Telegram của nhóm |

Transcript: `starter_v0/transcripts/v3_openrouter_20261110T191419801552.transcript.json` (provider `openrouter`, model `openai/gpt-4o-mini`, `artifact_version` = `v3+pba7bced2b20e+t447fb12c0244`). Transcript chạy trên bản tích hợp (prompt/tools v3 + 4 tool mới của nhóm), nên `tools_hash` khác run eval v3.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item                                 | Evidence File                | What Worked | Risk / Guardrail |
| ------------------------------------ | ---------------------------- | ----------- | ---------------- |
| Tool mới (`tools/<tên>/`)        |                              |             |                  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |             |                  |
| UI (lệnh chạy + link dùng thử)   | `starter_v0/web_app.py`, `starter_v0/web/index.html`, `starter_v0/artifacts/versions/`; lệnh `python web_app.py`; link ở mục A1 | Gọi agent thật; chọn model và version v0–v3/`current`; chế độ Compare 2 version; hiện tool call, args, kết quả, lỗi tool; mỗi chat lưu transcript `ui_*.transcript.json` | Cổng xác nhận trên UI: kể cả khi model gọi `send(confirmed=true)`, không gửi gì cho tới khi người dùng bấm xác nhận. Giới hạn 15 lượt/chat và 300 lượt/server để link public không dùng hết credit API. Snapshot v0–v3 có hash khớp run JSON. Rủi ro: link tunnel tạm thời; `reading_list` lưu chung một file cho mọi người dùng |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus                                            | Evidence File                                                                              | What Worked                                                                                                                                                        | Risk / Guardrail                                                                                                                                                  |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Small Local Model                                | xem B7                                                                                     |                                                                                                                                                                    |                                                                                                                                                                   |
| Hơn 3 tool mới (≥ 4)                          |                                                                                            |                                                                                                                                                                    |                                                                                                                                                                   |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/v3_openrouter_20261110T191419801552.transcript.json` (turn 4–5) | Agent hỏi `clarify(response_type="yes_no")` → user "Có, đăng đi" → `send(confirmed=true)` → `status: sent`; tin đã lên private channel của nhóm | Tool `send` tự chặn khi `confirmed=false` (trả `needs_confirmation`, không gọi Telegram API); prompt v3 cấm gọi `send` trước khi user xác nhận |
| Test challenge (0 skipped / regression test)     | `pytest` output                                                                          |                                                                                                                                                                    |                                                                                                                                                                   |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version          | Model (provider)                                | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File                                                                        |
| ---------------- | ----------------------------------------------- | ------------ | ------------- | ------------ | -------- | --------- | ------------------------------------------------------------------------------- |
| v0               | `openai/gpt-4o-mini` (openrouter)             | v0           | 0.65          | 0.75         | 0.65     | 1.00      | `starter_v0/runs/v0_B_base_openrouter_20261110T170619040358.json`             |
| v0-local-qwen3b  | `qwen2.5:3b` (ollama)                         | v0           | 0.35          | 0.50         | 0.35     | 0.50      | `starter_v0/runs/v0-local-qwen3b_B_base_ollama_20261110T184218499398.json`    |
| v0-local-llama3b | `llama3.2:3b` (ollama)                        | v0           | 0.15          | 0.20         | 0.15     | 0.17      | `starter_v0/runs/v0-local-llama3b_B_base_ollama_20261110T184443662952.json`   |
| v0-local-qwen7b  | `qwen2.5:7b` (ollama)                         | v0           | 0.35          | 0.45         | 0.35     | 0.50      | `starter_v0/runs/v0-local-qwen7b_B_base_ollama_20261110T191142426377.json`    |
| v3               | `openai/gpt-4o-mini` (openrouter)             | v3           | 0.95          | 1.00         | 0.95     | 1.00      | `starter_v0/runs/v3_B_base_openrouter_20261110T190626530147.json`             |
| v3-qwen3b        | `qwen2.5:3b` (ollama)                         | v3           | 0.65          | 0.75         | 0.65     | 0.83      | `starter_v0/runs/v3-qwen3b_B_base_ollama_20261110T191336357156.json`          |
| v3-llama3b       | `llama3.2:3b` + `num_predict=1024` (ollama) | v3           | 0.25          | 0.55         | 0.25     | 0.17      | `starter_v0/runs/v3-llama3b_B_base_ollama_20261110T193048778497.json`         |
| v3-qwen7b        | `qwen2.5:7b` (ollama)                         | v3           | 0.70          | 0.85         | 0.70     | 0.83      | `starter_v0/runs/v3-qwen7b_B_base_ollama_20261110T193528351027.json`          |
| v4-local-qwen3b  | `qwen2.5:3b` (ollama)                         | v4-local     | 0.55          | 0.65         | 0.55     | 0.83      | `starter_v0/runs/v4-local-qwen3b_B_base_ollama_20261110T193809429533.json`    |
| v4-local-llama3b | `llama3.2:3b` + `num_predict=1024` (ollama) | v4-local     | 0.20          | 0.50         | 0.20     | 0.17      | `starter_v0/runs/v4-local-llama3b_B_base_ollama_20261110T194143079805.json`   |
| v4-local-qwen7b  | `qwen2.5:7b` (ollama)                         | v4-local     | 0.70          | 0.80         | 0.70     | 0.83      | `starter_v0/runs/v4-local-qwen7b_B_base_ollama_20261110T194640936316.json`    |
| v5-local-qwen3b  | `qwen2.5:3b` (ollama)                         | v5-local     | 0.40          | 0.60         | 0.40     | 0.33      | `starter_v0/runs/v5-local-qwen3b_B_base_ollama_20261110T195042899445.json`    |
| v5-local-llama3b | `llama3.2:3b` + `num_predict=1024` (ollama) | v5-local     | 0.15          | 0.45         | 0.15     | 0.17      | `starter_v0/runs/v5-local-llama3b_B_base_ollama_20261110T195343037570.json`   |
| v5-local-qwen7b  | `qwen2.5:7b` (ollama)                         | v5-local     | 0.60          | 0.80         | 0.60     | 0.67      | `starter_v0/runs/v5-local-qwen7b_B_base_ollama_20261110T195706724093.json`    |
| v5-local-cloud   | `openai/gpt-4o-mini` (openrouter)             | v5-local     | 0.90          | 0.95         | 0.90     | 1.00      | `starter_v0/runs/v5-local-cloud_B_base_openrouter_20261110T194756575137.json` |

Hai vòng tối ưu cho local (mỗi vòng một giả thuyết, đều xuất phát từ v3):

- **v4-local** (`artifacts/system_prompt_local_v4.md` + `artifacts/tools_local_v4.yaml` = tools v3). Giả thuyết: model nhỏ biết cần hỏi lại nhưng viết câu hỏi thành text thay vì gọi `clarify` (R10/R11/R12 của `v3-qwen3b` đều trả text, 0 tool call), nên thêm một khối "hỏi người dùng là TOOL CALL" + 2 ví dụ gọi `clarify` (tình huống khác với case eval). Kết quả: không sửa được R10–R12; `qwen2.5:3b` còn gọi `clarify` cho cả request ngoài phạm vi (R14) và bỏ gọi tool ở R04 → 0.65 → 0.55; `llama3.2:3b` 0.25 → 0.20; `qwen2.5:7b` giữ 0.70.
- **v5-local** (`artifacts/system_prompt_local_v5.md` + `artifacts/tools_local_v5.yaml`). Giả thuyết: prompt + tools v3 quá dài (~1.650 từ) khiến model nhỏ bị nhiễu thông tin, nên rút gọn còn ~610 từ (5 rule ngắn, mỗi tool một dòng, giữ nguyên tên tool/args/enum). Kết quả: cả 3 model đều tụt so với v3 (`qwen2.5:3b` 0.40, `llama3.2:3b` 0.15, `qwen2.5:7b` 0.60), lỗi `wrong_arg_value` tăng (`qwen2.5:3b` 3 → 5). Kiểm tra ngược trên cloud: 0.90 (v3 là 0.95), chỉ thêm 1 lỗi ở R10 (`social_search(query="")` thay vì `clarify`, vì bản rút gọn bỏ câu "không gọi social_search với query rỗng").

Phần cứng chạy local: Apple M1 (GPU 8 core), 16 GB unified memory, Ollama 0.40.16. Dòng `v0-local-*` là đo thêm trên cùng prompt v0, để so cloud và local khi prompt chưa tối ưu. Với prompt v3, `llama3.2:3b` bị lỗi sinh lặp không dừng ở một case (~12.700 token, request timeout 10 phút rồi retry). Run không có giới hạn sẽ ra `provider_error` (không hợp lệ), nên `v3-llama3b` trở đi chạy bằng biến thể Ollama `llama3.2:3b-cap1024`: cùng trọng số, chỉ thêm `PARAMETER num_predict 1024`.

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern                                 | Count                                                                 | Example Case                                                                                                                   | Fix Tried                                                          | Helped?                                                                   |
| ----------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| wrong / hallucinated tool                       | v3: qwen3b 2, llama3b 6, qwen7b 0 (không có tool bịa tên)         | R07: "tweet phổ biến về OpenAI" → `timeline(screenname="OpenAI")` thay vì `social_search(search_type="Top")` (qwen3b) | v5-local: rút gọn description, ghi rõ BY account vs ABOUT topic | Không: v5 tăng lên qwen3b 4, llama3b 8                                 |
| wrong arg value                                 | v3: qwen3b 3, llama3b 6, qwen7b 3                                     | R13: `timeframe="today"` (enum là `day`); M03: bịa handle `andrejkarcharya` (qwen3b)                                   | v5-local: giữ enum, bỏ giải thích dài                         | Không: qwen3b 3 → 5, qwen7b 3 → 4                                      |
| invalid JSON args (`_invalid_json_arguments`) | 0 ở mọi run local                                                   | —                                                                                                                             | —                                                                 | —                                                                        |
| no tool call / answered directly                | v3: qwen3b 3, llama3b 1, qwen7b 3                                     | R11: trả text "Tôi cần biết URL của bài viết…" thay vì gọi tool (qwen3b)                                             | v4-local: rule "hỏi người dùng là TOOL CALL" + 2 ví dụ      | Không: qwen3b vẫn 3, qwen7b 3 → 2                                      |
| missed `clarify`                              | v3: qwen3b 3, llama3b 3, qwen7b 2                                     | R10/R11/R12                                                                                                                    | v4-local (như trên)                                              | Không: 3 / 3 / 3 ở v4; còn gây gọi `clarify` thừa ở R14 (qwen3b) |
| repeated / unnecessary calls                    | 0 lặp cùng tool; 1 gọi thừa (`clarify` ở R14, v4-local-qwen3b) | R14                                                                                                                            | —                                                                 | —                                                                        |
| sinh lặp không dừng (runaway generation)     | 1 case, `llama3.2:3b` với prompt v3                                | ~12.700 token, timeout 10 phút                                                                                                | `num_predict=1024` trong Ollama                                  | Có: run hợp lệ (0 provider_error)                                      |

- **Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?** Prompt + tool declaration rõ ràng, chi tiết (bản v3 của nhóm): cùng model, đổi từ v0 sang v3 nâng `qwen2.5:3b` 0.35 → 0.65, `qwen2.5:7b` 0.35 → 0.70, `llama3.2:3b` 0.15 → 0.25. Cả hai hướng tối ưu riêng cho local đều làm tụt điểm: thêm rule nhấn mạnh (v4) làm model gọi `clarify` quá đà, còn rút gọn (v5) làm mất quy ước args. Yếu tố thứ hai là kích thước/dòng model: `qwen2.5` tốt hơn hẳn `llama3.2` cùng cỡ 3B, và 7B chỉ hơn 3B một chút (0.70 vs 0.65 ở v3).
- **Bản prompt tối ưu cho local chạy trên model cloud thì sao?** `v5-local` trên `gpt-4o-mini` đạt 0.90 so với 0.95 của v3 (chỉ thêm 1 lỗi ở R10). Cloud chịu được bản rút gọn, nhưng bản rút gọn không giúp model local. V3 là bản dùng chung tốt nhất (cloud 0.95, `qwen2.5:7b` 0.70).
- **Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?** Khi dữ liệu không được rời máy (ví dụ tra cứu `policy` nội bộ), cần chạy offline, hoặc cần chạy rất nhiều mà không muốn tốn tiền API; và chỉ với tác vụ đơn giản, ít hành động ra ngoài (đọc timeline, tìm tin).

## 5. Khó khăn và cách xử lý

| Khó khăn                                                                   | Cách xử lý                                              |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `llama3.2:3b` sinh lặp không dừng ở một case (~12.700 token, timeout) | Chạy bằng biến thể `num_predict=1024`, ghi rõ ở B7 |

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo
