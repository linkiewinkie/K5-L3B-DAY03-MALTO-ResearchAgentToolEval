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

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
| ------- | ------------ | ----------------- | ----------- | --- |
|         |              |                   |             |     |

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
| v3-qwen3b | `qwen2.5:3b` (ollama) | v3 | 0.65 | 0.75 | 0.65 | 0.83 | `starter_v0/runs/v3-qwen3b_B_base_ollama_20261110T191336357156.json` |
| v3-llama3b | `llama3.2:3b` + `num_predict=1024` (ollama) | v3 | 0.25 | 0.55 | 0.25 | 0.17 | `starter_v0/runs/v3-llama3b_B_base_ollama_20261110T193048778497.json` |
| v3-qwen7b | `qwen2.5:7b` (ollama) | v3 | 0.70 | 0.85 | 0.70 | 0.83 | `starter_v0/runs/v3-qwen7b_B_base_ollama_20261110T193528351027.json` |
| v4-local-qwen3b | `qwen2.5:3b` (ollama) | v4-local | 0.55 | 0.65 | 0.55 | 0.83 | `starter_v0/runs/v4-local-qwen3b_B_base_ollama_20261110T193809429533.json` |
| v4-local-llama3b | `llama3.2:3b` + `num_predict=1024` (ollama) | v4-local | 0.20 | 0.50 | 0.20 | 0.17 | `starter_v0/runs/v4-local-llama3b_B_base_ollama_20261110T194143079805.json` |
| v4-local-qwen7b | `qwen2.5:7b` (ollama) | v4-local | 0.70 | 0.80 | 0.70 | 0.83 | `starter_v0/runs/v4-local-qwen7b_B_base_ollama_20261110T194640936316.json` |
| v5-local-qwen3b | `qwen2.5:3b` (ollama) | v5-local | 0.40 | 0.60 | 0.40 | 0.33 | `starter_v0/runs/v5-local-qwen3b_B_base_ollama_20261110T195042899445.json` |
| v5-local-llama3b | `llama3.2:3b` + `num_predict=1024` (ollama) | v5-local | 0.15 | 0.45 | 0.15 | 0.17 | `starter_v0/runs/v5-local-llama3b_B_base_ollama_20261110T195343037570.json` |
| v5-local-qwen7b | `qwen2.5:7b` (ollama) | v5-local | 0.60 | 0.80 | 0.60 | 0.67 | `starter_v0/runs/v5-local-qwen7b_B_base_ollama_20261110T195706724093.json` |
| v5-local-cloud | `openai/gpt-4o-mini` (openrouter) | v5-local | 0.90 | 0.95 | 0.90 | 1.00 | `starter_v0/runs/v5-local-cloud_B_base_openrouter_20261110T194756575137.json` |

Hai vòng tối ưu cho local (mỗi vòng một giả thuyết, đều xuất phát từ v3):

- **v4-local** (`artifacts/system_prompt_local_v4.md` + `artifacts/tools_local_v4.yaml` = tools v3). Giả thuyết: model nhỏ biết cần hỏi lại nhưng viết câu hỏi thành text thay vì gọi `clarify` (R10/R11/R12 của `v3-qwen3b` đều trả text, 0 tool call), nên thêm một khối "hỏi người dùng là TOOL CALL" + 2 ví dụ gọi `clarify` (tình huống khác với case eval). Kết quả: không sửa được R10–R12; `qwen2.5:3b` còn gọi `clarify` cho cả request ngoài phạm vi (R14) và bỏ gọi tool ở R04 → 0.65 → 0.55; `llama3.2:3b` 0.25 → 0.20; `qwen2.5:7b` giữ 0.70.
- **v5-local** (`artifacts/system_prompt_local_v5.md` + `artifacts/tools_local_v5.yaml`). Giả thuyết: prompt + tools v3 quá dài (~1.650 từ) khiến model nhỏ bị nhiễu thông tin, nên rút gọn còn ~610 từ (5 rule ngắn, mỗi tool một dòng, giữ nguyên tên tool/args/enum). Kết quả: cả 3 model đều tụt so với v3 (`qwen2.5:3b` 0.40, `llama3.2:3b` 0.15, `qwen2.5:7b` 0.60), lỗi `wrong_arg_value` tăng (`qwen2.5:3b` 3 → 5). Kiểm tra ngược trên cloud: 0.90 (v3 là 0.95), chỉ thêm 1 lỗi ở R10 (`social_search(query="")` thay vì `clarify`, vì bản rút gọn bỏ câu "không gọi social_search với query rỗng").

Phần cứng chạy local: Apple M1 (GPU 8 core), 16 GB unified memory, Ollama 0.40.16. Dòng `v0-local-*` là đo thêm trên cùng prompt v0, để so cloud và local khi prompt chưa tối ưu. Với prompt v3, `llama3.2:3b` bị lỗi sinh lặp không dừng ở một case (~12.700 token, request timeout 10 phút rồi retry). Run không có giới hạn sẽ ra `provider_error` (không hợp lệ), nên `v3-llama3b` trở đi chạy bằng biến thể Ollama `llama3.2:3b-cap1024`: cùng trọng số, chỉ thêm `PARAMETER num_predict 1024`.

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern                                 | Count | Example Case | Fix Tried | Helped? |
| ----------------------------------------------- | ----- | ------------ | --------- | ------- |
| wrong / hallucinated tool                       | v3: qwen3b 2, llama3b 6, qwen7b 0 (không có tool bịa tên) | R07: "tweet phổ biến về OpenAI" → `timeline(screenname="OpenAI")` thay vì `social_search(search_type="Top")` (qwen3b) | v5-local: rút gọn description, ghi rõ BY account vs ABOUT topic | Không: v5 tăng lên qwen3b 4, llama3b 8 |
| wrong arg value                                 | v3: qwen3b 3, llama3b 6, qwen7b 3 | R13: `timeframe="today"` (enum là `day`); M03: bịa handle `andrejkarcharya` (qwen3b) | v5-local: giữ enum, bỏ giải thích dài | Không: qwen3b 3 → 5, qwen7b 3 → 4 |
| invalid JSON args (`_invalid_json_arguments`) | 0 ở mọi run local | — | — | — |
| no tool call / answered directly                | v3: qwen3b 3, llama3b 1, qwen7b 3 | R11: trả text "Tôi cần biết URL của bài viết…" thay vì gọi tool (qwen3b) | v4-local: rule "hỏi người dùng là TOOL CALL" + 2 ví dụ | Không: qwen3b vẫn 3, qwen7b 3 → 2 |
| missed `clarify`                              | v3: qwen3b 3, llama3b 3, qwen7b 2 | R10/R11/R12 | v4-local (như trên) | Không: 3 / 3 / 3 ở v4; còn gây gọi `clarify` thừa ở R14 (qwen3b) |
| repeated / unnecessary calls                    | 0 lặp cùng tool; 1 gọi thừa (`clarify` ở R14, v4-local-qwen3b) | R14 | — | — |
| sinh lặp không dừng (runaway generation)       | 1 case, `llama3.2:3b` với prompt v3 | ~12.700 token, timeout 10 phút | `num_predict=1024` trong Ollama | Có: run hợp lệ (0 provider_error) |


- **Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?** Prompt + tool declaration rõ ràng, chi tiết (bản v3 của nhóm): cùng model, đổi từ v0 sang v3 nâng `qwen2.5:3b` 0.35 → 0.65, `qwen2.5:7b` 0.35 → 0.70, `llama3.2:3b` 0.15 → 0.25. Cả hai hướng tối ưu riêng cho local đều làm tụt điểm: thêm rule nhấn mạnh (v4) làm model gọi `clarify` quá đà, còn rút gọn (v5) làm mất quy ước args. Yếu tố thứ hai là kích thước/dòng model: `qwen2.5` tốt hơn hẳn `llama3.2` cùng cỡ 3B, và 7B chỉ hơn 3B một chút (0.70 vs 0.65 ở v3). 
- **Bản prompt tối ưu cho local chạy trên model cloud thì sao?** `v5-local` trên `gpt-4o-mini` đạt 0.90 so với 0.95 của v3 (chỉ thêm 1 lỗi ở R10). Cloud chịu được bản rút gọn, nhưng bản rút gọn không giúp model local. V3 là bản dùng chung tốt nhất (cloud 0.95, `qwen2.5:7b` 0.70).
- **Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?** Khi dữ liệu không được rời máy (ví dụ tra cứu `policy` nội bộ), cần chạy offline, hoặc cần chạy rất nhiều mà không muốn tốn tiền API; và chỉ với tác vụ đơn giản, ít hành động ra ngoài (đọc timeline, tìm tin).

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
