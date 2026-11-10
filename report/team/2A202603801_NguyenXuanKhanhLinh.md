# Báo cáo cá nhân — NguyenXuanKhanhLinh-2A202603801

## 1. Thông tin thành viên

- Họ tên: Nguyễn Xuân Khánh Linh
- MSSV: 2A202603801
- Email: [nxklinh@gmail.com](mailto:nxklinh@gmail.com)

## 2. Phần việc phụ trách

Vai trò trong nhóm: **Nhóm trưởng — UI + Group Eval + điều phối**.

- Setup repo nhóm, chạy baseline v0 và phân tích lỗi (CP1).
- Viết 10 eval case nhóm `starter_v0/data/eval_group.json` và chạy group eval (CP4).
- Làm UI cho agent, gọi agent thật, có link dùng thử (CP5).
- Điều phối: chia branch, review và merge, tổng hợp việc còn thiếu trước khi nộp.

## 3. Đóng góp cụ thể

**Baseline v0 và phân tích lỗi**

- Chạy base eval v0 bằng OpenRouter (`openai/gpt-4o-mini`): 13/20 PASS, case accuracy 0.65, routing 0.75, argument 0.65, multi-turn 1.00.
- Phân tích 7 case FAIL (bảng B2): 5/7 lỗi do 3 chỉ dẫn xấu cố ý trong prompt starter (đoán thay vì hỏi, tự gửi không xác nhận, ép một tool một bước), 2/7 lỗi do thiếu convention args của `lookup`. Đối chiếu với run v1–v3 để ghi version nào sửa được từng case; phát hiện R13 PASS ở v1 nhưng FAIL lại ở v2, và R12 vẫn FAIL ở v3.

**10 eval case nhóm**

- 5 single-turn + 5 multi-turn, phủ đủ 6 loại lỗi, có case route tới cả 4 tool mới của nhóm (`dedupe`, `filter_results`, `topic_stats`, `reading_list`).
- Thiết kế theo cách `run_eval.py` chấm: chỉ ghi các args có giá trị xác định, đặt danh sách bài vào turn `assistant` trước đó để kiểm tra các tool xử lý kết quả, không viết case kỳ vọng `send(confirmed=true)` vì eval chạy tool thật.
- Chạy thử trên bản tích hợp (prompt v3 + 14 tool): 9/10 PASS. Case GM04 FAIL cho thấy model tự gọi `reading_list(action="clear", confirmed=true)` mà không hỏi người dùng, tức guardrail `confirmed` trong tool bị vượt qua khi model tự điền cờ xác nhận.

**Web UI**

- `starter_v0/web_app.py` + `starter_v0/web/index.html`: gọi agent thật qua `chat.run_model_tool_loop`, mỗi cuộc chat lưu transcript riêng.
- Chọn model (`gpt-4o-mini`, `glm-5.3`) và chọn version prompt/tools v0–v3 hoặc bản tích hợp; chế độ Compare gửi cùng một câu cho 2 version và hiện 2 cột cạnh nhau, kèm bảng điểm eval của từng version.
- Hiển thị các bước tool, args, kết quả JSON, lỗi tool, trạng thái hỏi lại; nhãn "Không dùng tool" khi model tự trả lời; tooltip giải thích từng tool.
- Cổng xác nhận trên UI: kể cả khi model gọi `send(confirmed=true)`, không gửi gì cho tới khi người dùng bấm xác nhận.
- Snapshot prompt/tools của v0–v3 lấy đúng từ commit của từng version, hash khớp với `prompt_hash`/`tools_hash` trong run JSON.

**Điều phối**

- Tạo branch cho từng thành viên, đổi tên repo theo chuẩn, rà repo theo `SUBMISSION.md` và `RUBRIC.md`, soạn hướng dẫn chia việc còn thiếu cho từng người.

## 4. Bằng chứng

- File/commit/PR:
  - Commit `facfddd`: run v0 `starter_v0/runs/v0_B_base_openrouter_20261110T170619040358.json`
  - Commit `bd2ae57`: web UI (`starter_v0/web_app.py`, `starter_v0/web/index.html`, `starter_v0/artifacts/versions/`)
  - Commit `711f871`: `starter_v0/data/eval_group.json`
  - Commit `e8145cb`: bảng B2 trong `report/team/group_report.md`
  - Commit `6c8b74e`: `TEAM.md`
  - Run bản tích hợp `v3-int`: base `starter_v0/runs/v3-int_B_base_openrouter_20261110T213215560432.json` (19/20), group `starter_v0/runs/v3-int_B_group_openrouter_20261110T213256880386.json` (9/10); dòng `v3-int` trong `starter_v0/artifacts/version_log.csv`; bảng B3
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Claude (trợ lý lập trình AI) để đọc code harness (`run_eval.py`, `chat.py`), gợi ý cách viết eval case, viết code web UI và soạn nháp bảng B2.
  - Tự kiểm tra: đối chiếu từng số liệu và tool call trong B2 với run JSON v0–v3; kiểm tra hash của snapshot v0–v3 khớp với run JSON; kiểm tra cấu trúc `eval_group.json` (5+5, `phase`, `failure_type`) và chạy `pytest` (0 failed); chạy thử group eval và đọc `actual_tool_calls` của từng case trước khi giữ hay sửa case; chạy UI với agent thật và kiểm tra transcript ghi đúng.

## 5. Tự đánh giá

- Hoàn thành các phần được giao: baseline v0 và phân tích lỗi, 10 eval case nhóm, web UI chạy agent thật, điều phối repo.
- Điểm làm tốt: các phân tích đều dựa trên run JSON thật; eval nhóm phát hiện được một lỗi guardrail thật (GM04) mà bộ base không có.
- Cần cải thiện: commit code sớm hơn (UI từng bị cất vào stash khi đổi branch), và chốt sớm hơn thứ tự tích hợp giữa tool mới và các version prompt để số liệu v3 và bản tích hợp không bị lệch.
