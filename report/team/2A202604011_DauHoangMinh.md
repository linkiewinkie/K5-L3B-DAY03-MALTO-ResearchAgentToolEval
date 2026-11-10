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

## 4. Bằng chứng

- Commit `d56cd74` (branch `hoangminh`): thêm backend service và unit test.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: ...

## 5. Tự đánh giá

- Hoàn thành tốt các phần việc được giao, phối hợp và thảo luận với teammate để đưa ra kết quả hoàn chỉnh
