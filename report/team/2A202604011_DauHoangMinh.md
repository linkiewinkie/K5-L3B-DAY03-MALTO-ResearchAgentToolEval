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

- Dựng backend service cho agent (`starter_v0/agent_backend.py`): UI chỉ cần gọi một hàm để chat với agent thật qua nhiều lượt. Kết quả mỗi lượt gồm câu trả lời, các tool đã gọi và trạng thái (đã trả lời / đang hỏi lại / chờ xác nhận trước khi gửi / lỗi). Mọi lượt đều được lưu transcript.
- Viết unit test cho backend (`starter_v0/tests/test_agent_backend.py`), chạy offline, không cần API key.
- Live chat v3 (5 lượt): yêu cầu thường, thiếu tài khoản → agent hỏi lại → bổ sung, yêu cầu đăng Telegram → agent hỏi xác nhận → gửi thật.
- Bonus Telegram: cấu hình bot và channel riêng của nhóm; agent chỉ gọi `send(confirmed=true)` sau khi người dùng xác nhận, trả về `status: sent`.
- Bonus Small Local Model: chạy base eval trên `qwen2.5:3b`, `llama3.2:3b`, `qwen2.5:7b` với prompt v0 và v3, thêm 2 vòng tối ưu (v4-local, v5-local) và kiểm tra ngược trên cloud. 

## 4. Bằng chứng

- Commit: `6aab420` (backend + unit test, trên `main`), `e84e62a`, `8918ad2` và `2355c73` (kết quả local model).
- Transcript live chat và Telegram: `starter_v0/transcripts/v3_openrouter_20261110T191419801552.transcript.json`.
- Run local: `starter_v0/runs/v0-local-*`, `v3-qwen3b/llama3b/qwen7b_*`, `v4-local-*`, `v5-local-*`; các dòng tương ứng trong `starter_v0/artifacts/version_log.csv`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Dùng AI để hỗ trợ kiểm tra lại phần code và đối chiếu lại số liệu evaluation

## 5. Tự đánh giá

- Hoàn thành tốt các phần việc được giao, phối hợp và thảo luận với teammate để đưa ra kết quả hoàn chỉnh
