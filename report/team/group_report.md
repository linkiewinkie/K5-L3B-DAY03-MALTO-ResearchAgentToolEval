# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (tools/<tên>/) | `starter_v0/tools/dedupe/`, `filter_results/`, `topic_stats/`, `reading_list/` (mỗi folder có `tool.py` + `TOOL.md`); đăng ký trong `tools/__init__.py`, khai báo trong `artifacts/tools.yaml` | 4 tool chạy local, không gọi mạng, nhận kết quả của `lookup/social_search` làm đầu vào. <br>• `dedupe`: gộp URL (bỏ `www`, `/` cuối, khác hoa thường). <br>• `filter_results`: lọc theo nguồn và theo ngày. <br>• `topic_stats`: đếm chủ đề (tự động hoặc theo danh sách người dùng nêu). <br>• `reading_list`: lưu bài vào file JSON local. | Tool lỗi đều trả error dict, không raise. <br>• `reading_list`: chỉ xoá toàn bộ khi `confirmed=true` và không ghi đè file JSON bị hỏng. <br>• `filter_results`: loại item không có ngày hợp lệ khi đặt `days`. |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed): `python -m pytest -q` → 131 passed, 0 skipped; `tests/test_tools_todo.py` | 33 test cho 4 tool mới (`dedupe` 8, `filter_results` 9, `topic_stats` 8, `reading_list` 8). Mỗi tool có happy path, input xấu (`None`, sai kiểu, `limit` dạng chuỗi) và nhánh lỗi. Tất cả chạy offline. | Test không gọi mạng thật (`block_network` chặn). `test_tool_contract.py` xanh (75 passed) nên khai báo, registry và code khớp nhau. |
| UI (lệnh chạy + link dùng thử) | (nhóm trưởng điền) | | |

Tool unit tests: đã viết 33 test cho 4 tool mới và điền toàn bộ 14 stub TODO của 8 tool có sẵn (tổng 131 test, 0 skipped). Ví dụ lỗi unit test bắt được mà eval không bắt được: reading_list khi file JSON bị hỏng phải trả error dict và không ghi đè file (test_reading_list_corrupted_file_returns_error_dict_and_is_not_overwritten). Eval chỉ đo model chọn tool nào và truyền args gì, nên không thấy được việc mất dữ liệu ở bước thực thi tool.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) | `starter_v0/tools/{dedupe,filter_results,topic_stats,reading_list}/`, `tests/test_tools_todo.py`, eval case: (điền id case sau khi nhóm trưởng thêm vào eval_group.json) | 4 tool tự viết, mỗi tool đủ `TOOL.md`, đăng ký, khai báo và 8–9 test. | Rubric đòi có eval case route tới mỗi tool, hiện chưa có case nào. Cần ≥ 4 case (hoặc case multi-turn gọi nhiều tool). || `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge | `pytest` output: 131 passed, 0 skipped. Regression test trong `tests/test_tools_todo.py` | 0 skipped, và đã tìm ra 2 bug ở tool có sẵn, đều có test regression. | Xem mô tả dưới. |

Tìm được 2 bug trong tool có sẵn.

1. `timeline` và `social_search`: `limit=-1` làm `items[:-1]` bỏ mất tweet cuối. Đã sửa bằng cách limit âm dùng mặc định 5. Test: `test_regression_negative_limit_does_not_slice_from_the_end` (2 tham số).
2. `format`: `items` chứa phần tử không phải dict (chuỗi, `None`, số) làm `AttributeError` thoát ra vòng lặp agent. Đã sửa bằng cách bỏ qua phần tử không phải dict. Test: `test_regression_format_skips_non_dict_items_instead_of_raising`. Cả 3 test fail trên code cũ và pass trên code đã sửa.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
