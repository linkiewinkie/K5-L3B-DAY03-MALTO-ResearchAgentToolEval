# Team

## Thông tin nhóm

- Tên nhóm: MALTO
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-MALTO-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/linkiewinkie/K5-L3B-DAY03-MALTO-ResearchAgentToolEval
- Nhánh nộp: `main`
- Commit chốt: <điền sau khi merge cuối>

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Xuân Khánh Linh | 2A202603801 | [nxklinh@gmail.com](mailto:nxklinh@gmail.com) | [linkiewinkie](https://github.com/linkiewinkie) | Nhóm trưởng — UI + Group Eval + điều phối |
|   2 | Đậu Hoàng Minh | 2A202604011 | [26ai.minhdh4@vinuni.edu.vn](mailto:26ai.minhdh4@vinuni.edu.vn) | [justapea25](https://github.com/justapea25) | Backend Integration + Live Chat + Report |
|   3 | Nguyễn Văn Lên | 2A202604007 | [26ai.lennv@vinuni.edu.vn](mailto:26ai.lennv@vinuni.edu.vn) | [Nguyenvanlen2412](https://github.com/Nguyenvanlen2412) | Prompt Engineering + tối ưu v1–v3 |
|   4 | Đặng Minh Thu | 2A202604009 | [26ai.thudm@vinuni.edu.vn](mailto:26ai.thudm@vinuni.edu.vn) | [minhthu27](https://github.com/minhthu27) | Custom Tool + Unit Testing |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## NguyenXuanKhanhLinh-2A202603801

### Phần việc phụ trách

- Chạy baseline v0 và phân tích lỗi (CP1).
- Viết 10 eval case nhóm và chạy group eval (CP4).
- Làm web UI gọi agent thật (CP5).
- Điều phối repo, branch, review và merge.

### Đóng góp cụ thể

- Chạy base eval v0 bằng OpenRouter (`openai/gpt-4o-mini`): 13/20 PASS, case accuracy 0.65; phân tích 7 case FAIL (bảng B2).
- Viết `starter_v0/data/eval_group.json`: 10 case (5 single-turn + 5 multi-turn), phủ đủ 6 loại lỗi và route tới cả 4 tool mới.
- Làm web UI (`starter_v0/web_app.py`, `starter_v0/web/index.html`): gọi agent thật, đổi model và version v0–v3, chế độ Compare, hiển thị tool call/lỗi, cổng xác nhận trước khi gửi Telegram.

### Bằng chứng

- Commit `facfddd` — `starter_v0/runs/v0_B_base_openrouter_20261110T170619040358.json`
- Commit `bd2ae57` — web UI + `starter_v0/artifacts/versions/`
- Commit `711f871` — `starter_v0/data/eval_group.json`
- Commit `e8145cb` — bảng B2 trong `report/team/group_report.md`

## DauHoangMinh-2A202604011

### Phần việc phụ trách

- Backend Integration + Live Chat + Report.
- Bonus: gửi Telegram có xác nhận, Small Local Model (Ollama).

### Đóng góp cụ thể

- Viết backend service cho agent (`starter_v0/agent_backend.py`) kèm unit test.
- Chạy live chat v3 (5 lượt: hỏi lại khi thiếu thông tin, xác nhận rồi gửi Telegram thật).
- Chạy eval trên 3 model local (`qwen2.5:3b`, `llama3.2:3b`, `qwen2.5:7b`) với prompt v0, v3 và 2 vòng tối ưu v4-local, v5-local.
- Tổng hợp báo cáo nhóm: B4, B5 (Telegram, local model), B7, mục 3, 5, 8 và B6.

### Bằng chứng

- Commit `6aab420` (backend + unit test), `2355c73` (kết quả local model)
- Transcript: `starter_v0/transcripts/v3_openrouter_20261110T191419801552.transcript.json`
- Run local: `starter_v0/runs/v{0,3,4,5}-local-*`, `v3-{qwen3b,llama3b,qwen7b}_*`
- Báo cáo cá nhân: `report/team/2A202604011_DauHoangMinh.md`

## NguyenVanLen-2A202604007

### Phần việc phụ trách

- Phân tích nguyên nhân lỗi ở baseline v0, thiết kế chu trình tối ưu qua 3 version v1–v3 (CP2).
- Tối ưu `starter_v0/artifacts/system_prompt.md`: loại bỏ chỉ dẫn xấu, thiết lập scope boundary, no-tool cho out-of-scope, thêm rule `clarify` khi thiếu thông tin và cổng xác nhận yes/no trước khi `send`.
- Tối ưu `starter_v0/artifacts/tools.yaml`: viết lại toàn bộ phần mô tả tool (khi nào dùng / không dùng) và chuẩn hóa argument conventions, enum format.
- Ghi log các vòng lặp vào `starter_v0/artifacts/version_log.csv`.

### Đóng góp cụ thể

- Version v1: Bỏ ép đoán thông tin, bỏ ép 1 bước, bỏ tự ý gửi; thêm scope research và cấm gọi tool cho câu hỏi toán/code. Base eval tăng từ 0.65 lên 0.80 (16/20 PASS).
- Version v2: Thêm rule hỏi lại bằng `clarify` khi thiếu handle/URL và rule xác nhận yes/no trước khi `send`. Base eval đạt 0.75 (15/20 PASS, phát hiện hạn chế khi chỉ sửa prompt).
- Version v3: Tinh chỉnh routing nguồn trong prompt + viết lại toàn diện `tools.yaml` (ranh giới dùng tool, convention `lookup`, `timeline`, `send`). Base eval nhảy vọt lên 0.95 (19/20 PASS, routing 1.00, args 0.95, multi-turn 1.00).

### Bằng chứng

- Commit `772e614` — run v1: `starter_v0/runs/v1_B_base_openrouter_20261110T182732220052.json`
- Commit `7db0972` — run v2: `starter_v0/runs/v2_B_base_openrouter_20261110T184712806825.json`
- Commit `65bf68f` — run v3: `starter_v0/runs/v3_B_base_openrouter_20261110T190626530147.json`
- Dòng v1, v2, v3 trong `starter_v0/artifacts/version_log.csv`
- Bảng B1, Mục 3 và Mục 7 (B6) trong `report/team/group_report.md`

## DangMinhThu-2A202604009

### Phần việc phụ trách

- Custom Tool + Unit Testing (CP3), branch `minhthu`.
- Bonus "hơn 3 tool mới" và "test challenge".

### Đóng góp cụ thể

- Viết 4 tool mới: `dedupe`, `filter_results`, `topic_stats`, `reading_list` (mỗi tool có `tool.py`, `TOOL.md`, đăng ký trong `tools/__init__.py`, khai báo trong `artifacts/tools.yaml`).
- Viết 33 unit test cho 4 tool mới (happy path, input xấu, nhánh lỗi), chạy offline; điền 14 stub TODO của 8 tool có sẵn → `pytest` 138 passed, 0 skipped.
- Tìm và sửa 2 bug ở tool có sẵn (`limit` âm ở `timeline`/`social_search`; `format` crash khi item không phải dict), kèm test regression.
- Gửi contract 4 tool cho nhóm trưởng để viết eval case; điền mục B5a và B5 trong group report.

### Bằng chứng

- Tool: `starter_v0/tools/dedupe/`, `filter_results/`, `topic_stats/`, `reading_list/`
- Test: `starter_v0/tests/test_tools_todo.py`
- Commit (branch `minhthu`): `83d6d81`, `206140f`, `47c07d7`
- Báo cáo cá nhân: `report/team/2A202604009_DangMinhThu.md`
