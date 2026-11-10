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
pip install -r requirements.txt   # đã có streamlit
cp .env.example .env              # điền OPENROUTER_API_KEY, TAVILY_API_KEY, FIRECRAWL_API_KEY, RAPIDAPI_KEY
streamlit run app.py              # → http://localhost:8501
```

UI hiện câu trả lời của agent, từng tool call (tên tool, args, kết quả, lỗi nếu có), và một nút xác nhận khi agent muốn gửi Telegram. Mọi lượt chat được lưu vào `starter_v0/transcripts/`.

**Link dùng thử (deploy):**

Mở bằng Cloudflare Tunnel trong lúc demo: `cloudflared tunnel --url http://localhost:8501`. Link `trycloudflare.com` chỉ sống khi lệnh còn chạy, nên mỗi lần mở lại là một link mới.

> URL: _(dán link khi mở tunnel lúc showdown)_

### A2. Tool agent có

| Tên tool        | Làm được gì                                                                                       | Nguồn dữ liệu          | Tool mới nhóm thêm? |
| --------------- | -------------------------------------------------------------------------------------------------- | ---------------------- | ------------------- |
| `clarify`       | Hỏi lại người dùng khi thiếu thông tin (tài khoản, URL, chủ đề…); agent dừng chờ trả lời            | —                      | không               |
| `timeline`      | Lấy các bài đăng mới nhất của một tài khoản X/Twitter (handle không có `@`)                        | RapidAPI Twitter API45 | không               |
| `social_search` | Tìm bài đăng trên X/Twitter theo từ khoá (`Top` hoặc `Latest`)                                     | RapidAPI Twitter API45 | không               |
| `lookup`        | Tìm kiếm web / tin tức theo từ khoá, có lọc khoảng thời gian                                       | Tavily                 | không               |
| `fetch`         | Đọc nội dung một URL cụ thể (trả về text/markdown)                                                 | Firecrawl              | không               |
| `format`        | Trình bày các kết quả đã có thành bản tin có tiêu đề và link nguồn                                 | Local                  | không               |
| `send`          | Gửi bản tin lên Telegram; **chỉ gửi khi `confirmed=true`**, chưa xác nhận thì trả `needs_confirmation` | Telegram Bot API       | không               |
| `policy`        | Tra cứu tài liệu chính sách nội bộ (nghiên cứu AI, bảo mật dữ liệu, đăng bài ra ngoài, trích dẫn nguồn, dùng tool) | `company_policy/*.md`  | không (bonus có sẵn) |
| `papers`        | Tìm bài báo khoa học trên arXiv                                                                    | arXiv API              | không (bonus có sẵn) |
| `paper_text`    | Lấy nội dung text của một bài báo arXiv (đọc PDF)                                                  | arXiv + pypdf          | không (bonus có sẵn) |
| _(tool mới)_    | _Cập nhật khi tool mới của nhóm được tích hợp vào `tools.yaml`._                                    |                        | có                  |

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

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
| ------- | ---------------- | ---------- | ------------: | -----------: | -------- |
| v0      | baseline         |            |               |              |          |
| v1      |                  |            |               |              |          |
| v2      |                  |            |               |              |          |
| v3      |                  |            |               |              |          |

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

| Case ID | What It Tests | Expected Tool/Behavior | Result |
| ------- | ------------- | ---------------------- | ------ |
|         |               |                        |        |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
| ---- | ------------ | ---------- | ---------------- | ------- |
| 1 — yêu cầu thường | "Tin tức AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news", timeframe="day")` | v3 | ✅ Trả lời tóm tắt tin AI trong ngày, có nguồn |
| 2 — thiếu thông tin | "Tóm tắt 5 tweet mới nhất giúp mình" | `clarify(response_type="text")`: "Bạn muốn tóm tắt 5 tweet mới nhất từ tài khoản nào?" | v3 | ✅ Không đoán tài khoản, hỏi lại và giữ số lượng 5 |
| 3 — bổ sung thông tin | "Của Andrej Karpathy nhé" | `timeline(screenname="karpathy", limit=5)` | v3 | ✅ Đổi tên sang handle đúng, giữ `limit=5` từ lượt trước |
| 4 — yêu cầu gửi/đăng | "Đăng bản tin tóm tắt vừa rồi lên Telegram giúp mình" | `clarify(response_type="yes_no")`: "Bạn có muốn đăng nội dung tóm tắt tweet của Andrej Karpathy lên Telegram không?" | v3 | ✅ Không gửi ngay, hỏi xác nhận trước |
| 5 — xác nhận gửi | "Có, đăng đi" | `send(text=..., confirmed=true)` → `status: sent` | v3 | ✅ Chỉ gửi sau khi người dùng xác nhận; tin đã lên channel Telegram của nhóm |

Transcript: `starter_v0/transcripts/v3_openrouter_20261110T191419801552.transcript.json` (provider `openrouter`, model `openai/gpt-4o-mini`, `artifact_version` = `v3+pba7bced2b20e+t447fb12c0244`). Transcript chạy trên bản tích hợp (prompt/tools v3 + 4 tool mới của nhóm), nên `tools_hash` khác run eval v3.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item                                 | Evidence File                | What Worked | Risk / Guardrail |
| ------------------------------------ | ---------------------------- | ----------- | ---------------- |
| Tool mới (`tools/<tên>/`)        |                              |             |                  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |             |                  |
| UI (lệnh chạy + link dùng thử)   |                              |             |                  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus                                            | Evidence File     | What Worked | Risk / Guardrail |
| ------------------------------------------------ | ----------------- | ----------- | ---------------- |
| Small Local Model                                | xem B7            |             |                  |
| Hơn 3 tool mới (≥ 4)                          |                   |             |                  |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/v3_openrouter_20261110T191419801552.transcript.json` (turn 4–5) | Agent hỏi `clarify(response_type="yes_no")` → user "Có, đăng đi" → `send(confirmed=true)` → `status: sent`; tin đã lên private channel của nhóm | Tool `send` tự chặn khi `confirmed=false` (trả `needs_confirmation`, không gọi Telegram API); prompt v3 cấm gọi `send` trước khi user xác nhận |
| Test challenge (0 skipped / regression test)     | `pytest` output |             |                  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version            | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
| ------------------ | ---------------- | ------------ | ------------- | ------------ | -------- | --------- | -------- |
| v0 | `openai/gpt-4o-mini` (openrouter) | v0 | 0.65 | 0.75 | 0.65 | 1.00 | `starter_v0/runs/v0_B_base_openrouter_20261110T170619040358.json` |
| v0-local-qwen3b | `qwen2.5:3b` (ollama) | v0 | 0.35 | 0.50 | 0.35 | 0.50 | `starter_v0/runs/v0-local-qwen3b_B_base_ollama_20261110T184218499398.json` |
| v0-local-llama3b | `llama3.2:3b` (ollama) | v0 | 0.15 | 0.20 | 0.15 | 0.17 | `starter_v0/runs/v0-local-llama3b_B_base_ollama_20261110T184443662952.json` |
| v0-local-qwen7b | `qwen2.5:7b` (ollama) | v0 | 0.35 | 0.45 | 0.35 | 0.50 | `starter_v0/runs/v0-local-qwen7b_B_base_ollama_20261110T191142426377.json` |
| v3 | `openai/gpt-4o-mini` (openrouter) | v3 | 0.95 | 1.00 | 0.95 | 1.00 | `starter_v0/runs/v3_B_base_openrouter_20261110T190626530147.json` |
| v3-qwen3b | `qwen2.5:3b` (ollama) | v3 |  |  |  |  |  |
| v3-llama3b | `llama3.2:3b` (ollama) | v3 |  |  |  |  |  |
| v3-qwen7b | `qwen2.5:7b` (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Phần cứng chạy local: Apple M1 (GPU 8 core), 16 GB unified memory, Ollama 0.40.16. Dòng `v0-local-*` là đo thêm trên cùng prompt v0, để so cloud và local khi prompt chưa tối ưu.

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern                                 | Count | Example Case | Fix Tried | Helped? |
| ----------------------------------------------- | ----- | ------------ | --------- | ------- |
| wrong / hallucinated tool                       |       |              |           |         |
| invalid JSON args (`_invalid_json_arguments`) |       |              |           |         |
| no tool call / answered directly                |       |              |           |         |
| missed `clarify`                              |       |              |           |         |
| repeated / unnecessary calls                    |       |              |           |         |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo
