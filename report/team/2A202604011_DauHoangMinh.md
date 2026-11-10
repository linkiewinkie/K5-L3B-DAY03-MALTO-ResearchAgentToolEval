# Báo cáo cá nhân — DauHoangMinh-2A202604011

## 1. Thông tin thành viên

- Họ tên: Đậu Hoàng Minh
- MSSV: 2A202604011
- Email: [26ai.minhdh4@vinuni.edu.vn](mailto:26ai.minhdh4@vinuni.edu.vn)

## 2. Phần việc phụ trách

Vai trò trong nhóm: **Backend Integration + Live Chat + Report** (TV4).

- Viết lớp backend (`agent_backend.py`) để UI gọi agent thật, kèm unit test.
- Tích hợp prompt/tools v3 và tool mới của nhóm vào backend, chạy live chat và lưu transcript.
- Tổng hợp báo cáo nhóm (`report/team/group_report.md`).
- Bonus: gửi Telegram có xác nhận
- Bonus: Xem đo kết quả của Small Local Model (Ollama, Step 7).

## 3. Đóng góp cụ thể

### Backend service cho agent

- Viết `starter_v0/agent_backend.py`: UI chỉ cần tạo một session và gọi một hàm để chat với agent thật qua nhiều lượt, dùng lại vòng lặp model ↔ tool của `chat.py`.
- Mỗi lượt trả về câu trả lời, các tool đã gọi và trạng thái: đã trả lời / đang hỏi lại / chờ xác nhận trước khi gửi / hết số vòng tool / lỗi provider. Mọi lượt đều được lưu transcript.
- Viết 7 unit test (`starter_v0/tests/test_agent_backend.py`) dùng provider giả, chạy offline, không cần API key.
- Kiểm tra tích hợp nhánh của Thu (4 tool mới) và Lên (prompt/tools v3) vào backend trước khi gộp: không conflict, `pytest` xanh, chạy thử chat thật với `reading_list`.

### Live chat và gửi Telegram

- Cấu hình bot và private channel Telegram của nhóm.
- Chạy live chat 5 lượt trên bản v3: hỏi tin tức → yêu cầu thiếu tài khoản thì agent hỏi lại → bổ sung tên, agent tự đổi sang handle `karpathy` và giữ `limit=5` → yêu cầu đăng Telegram thì agent hỏi xác nhận yes/no → đồng ý thì `send(confirmed=true)` trả về `status: sent`.

### Bonus Small Local Model (Ollama)

- Chạy base eval trên 3 model local (`qwen2.5:3b`, `llama3.2:3b`, `qwen2.5:7b`) với prompt v0 và v3 của nhóm, máy Apple M1 16 GB.
- Thử 2 vòng tối ưu riêng cho local, mỗi vòng một giả thuyết:

| Version | Giả thuyết | Kết quả |
|---|---|---|
| v3 (của nhóm) | Prompt/tools tối ưu cho cloud cũng giúp model nhỏ | `qwen2.5:3b` 0.35 → 0.65, `qwen2.5:7b` 0.35 → 0.70, `llama3.2:3b` 0.15 → 0.25 |
| v4-local | Model nhỏ hỏi lại bằng text thay vì gọi `clarify`; thêm rule + 2 ví dụ | Không tăng: 0.55 / 0.20 / 0.70 |
| v5-local | Prompt + tools quá dài (~1.650 từ); rút gọn còn ~610 từ | Tụt: 0.40 / 0.15 / 0.60; chạy trên cloud vẫn 0.90 |

- `llama3.2:3b` bị sinh lặp không dừng ở một case (~12.700 token, timeout), nên chạy bằng biến thể `num_predict=1024` để run hợp lệ.
- Ghi đủ các dòng vào `version_log.csv` và viết mục B7 trong báo cáo nhóm.

### Báo cáo nhóm

- Viết B4, B5 (Telegram, local model), B7, mục 3, 5, 8 và B6; đối chiếu số liệu với run JSON.

## 4. Bằng chứng

- Commit: `6aab420` (backend + unit test, trên `main`), `e84e62a`, `8918ad2` và `2355c73` (kết quả local model).
- Transcript live chat và Telegram: `starter_v0/transcripts/v3_openrouter_20261110T191419801552.transcript.json`.
- Run local: `starter_v0/runs/v0-local-*`, `v3-qwen3b/llama3b/qwen7b_*`, `v4-local-*`, `v5-local-*`; các dòng tương ứng trong `starter_v0/artifacts/version_log.csv`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Dùng AI để hỗ trợ kiểm tra lại phần code và đối chiếu lại số liệu evaluation

## 5. Tự đánh giá

**Làm tốt**

- Hoàn thành các phần việc được giao, phối hợp và thảo luận với teammate để đưa ra kết quả hoàn chỉnh.
- Backend có trạng thái rõ cho từng lượt (hỏi lại, chờ xác nhận), nên UI biết khi nào phải dừng chờ người dùng thay vì gửi Telegram luôn.
- Phần local model có đủ 3 model, 2 vòng tối ưu, mọi run đều hợp lệ (0 lỗi provider) và có ghi lại cả kết quả không tốt.

**Hạn chế**

- Cả 2 vòng tối ưu local đều không vượt được v3
- Live chat mới chạy trên một số kịch bản; chưa thử người dùng đổi nội dung giữa chừng.

**Bài học**

- Với model nhỏ, prompt dài nhưng rõ ràng tốt hơn prompt ngắn; thêm rule nhấn mạnh có thể làm model gọi tool quá đà.
- Guardrail cho hành động gửi ra ngoài cần có ở cả prompt, code tool và UI, không dựa vào một lớp.
- Kết quả chỉ nên ghi khi run hợp lệ; cần kiểm tra `provider_error_cases` trước khi đưa số vào báo cáo.
