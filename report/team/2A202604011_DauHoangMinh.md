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
- Bonus Telegram: kiểm tra bot và channel thử, gửi thử thành công qua tool `send`. Khi chưa xác nhận thì tool bị chặn, không gửi.
- Bonus Small Local Model (Ollama): cài Ollama, kéo các model local (`qwen2.5:3b`, `llama3.2:3b`), chạy base eval với prompt/tools v0 để so với cloud. Cùng prompt v0, `qwen2.5:3b` đạt case accuracy 0.35 và `llama3.2:3b` đạt 0.15, so với 0.65 của cloud `gpt-4o-mini`. Lỗi chủ yếu là chọn sai tool, sai args hoặc không gọi tool. Kết quả ghi ở mục B7 của báo cáo nhóm (`starter_v0/runs/v0-local-*.json`).

## 4. Bằng chứng

- Commit `d56cd74` (branch `hoangminh`): thêm backend service và unit test.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Dùng AI để hỗ trợ kiểm tra lại phần code và đối chiếu lại số liệu evaluation

## 5. Tự đánh giá

- Hoàn thành tốt các phần việc được giao, phối hợp và thảo luận với teammate để đưa ra kết quả hoàn chỉnh
