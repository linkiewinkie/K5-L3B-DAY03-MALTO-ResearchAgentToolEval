# Báo cáo cá nhân — NguyenVanLen-2A202604007

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Lên
- MSSV: 2A202604007
- Email: [26ai.lennv@vinuni.edu.vn](mailto:26ai.lennv@vinuni.edu.vn)
- GitHub: [Nguyenvanlen2412](https://github.com/Nguyenvanlen2412)

## 2. Phần việc phụ trách

Vai trò trong nhóm: **Prompt Engineering + tối ưu prompt & tool declaration v1–v3 (CP2)**.

- Phân tích nguyên nhân gốc của các lỗi ở baseline v0 (đặc biệt là 7 case FAIL do prompt starter ép sai hành vi).
- Thiết kế và thực hiện chu trình tối ưu lặp dựa trên bằng chứng (giả thuyết → sửa artifact → chạy eval đo lường → phân tích) qua 3 phiên bản: v1, v2, v3.
- Cải thiện `starter_v0/artifacts/system_prompt.md`: loại bỏ chỉ dẫn xấu, định nghĩa ranh giới vai trò (scope boundary), hành vi no-tool, cơ chế hỏi lại thông tin thiếu (`clarify`) và boundary xác nhận trước khi thực hiện hành động ra bên ngoài.
- Cải thiện `starter_v0/artifacts/tools.yaml`: viết lại toàn bộ phần mô tả tool (khi nào nên dùng và khi nào KHÔNG được dùng) và chuẩn hóa quy ước tham số (argument conventions, enum values, xử lý handle/URL).
- Ghi nhận đầy đủ log các vòng lặp vào `starter_v0/artifacts/version_log.csv`.

## 3. Đóng góp cụ thể

### Vòng 1 — Version v1: Làm sạch chỉ dẫn xấu và thiết lập ranh giới vai trò (Scope & Boundary)
- **Vấn đề v0**: Prompt starter cố ý chứa 3 chỉ dẫn xấu: (1) ép đoán thay vì hỏi ("make a sensible guess"), (2) ép hoàn thành trong 1 bước duy nhất ("finish in a single step, pick one tool"), (3) tự ý gửi tin nhắn không chờ ("just go ahead and do it"). Hậu quả: model tự bịa handle (`timeline`), bịa URL (`fetch`), và dùng `send` để trả lời cả bài toán tích phân hay viết code (R08, R14).
- **Giả thuyết**: Loại bỏ các chỉ dẫn đoán mò và ép 1 bước; định nghĩa rõ vai trò research assistant; yêu cầu từ chối trả lời không gọi tool với các tác vụ ngoài phạm vi (toán học, lập trình) sẽ ngăn chặn việc gọi tool sai và lạm dụng `send`.
- **Thay đổi**: Sửa `starter_v0/artifacts/system_prompt.md`:
  - Khẳng định vai trò research assistant (tìm và tóm tắt thông tin).
  - Thêm quy tắc: câu hỏi về năng lực/vai trò thì trả lời trực tiếp không gọi tool.
  - Quy định rõ phạm vi: các yêu cầu giải toán, viết code nằm ngoài phạm vi thì giải thích ngắn gọn, cấm gọi bất kỳ tool nào.
  - Giới hạn công cụ `send`: chỉ dùng khi người dùng yêu cầu rõ ràng, tuyệt đối không dùng `send` để trả lời câu hỏi thông thường.
- **Kết quả eval**: Case accuracy tăng từ **0.65 lên 0.80** (16/20 PASS). Đã sửa thành công 3 case FAIL: R03 (`lookup`), R08 (`out_of_scope` giải toán), R14 (`out_of_scope_coding`).

### Vòng 2 — Version v2: Bổ sung quy tắc hỏi lại khi thiếu thông tin và xác nhận hành động
- **Vấn đề v1**: Ở v1 model vẫn thất bại ở các case thiếu thông tin (R10 thiếu handle, R11 thiếu URL) do chưa có cơ chế hướng dẫn model dừng lại hỏi người dùng bằng `clarify`; đồng thời case R12 model vẫn tự gọi `send` mà không xin xác nhận.
- **Giả thuyết**: Bổ sung quy tắc tường minh: kiểm tra thông tin bắt buộc trước khi gọi tool, nếu thiếu handle/URL thì phải gọi `clarify` (giữ lại các chi tiết đã có); trước khi gửi ra ngoài phải gọi `clarify` dạng yes/no để xin xác nhận.
- **Thay đổi**: Thêm vào `starter_v0/artifacts/system_prompt.md`:
  - Rule: Kiểm tra thông tin bắt buộc trước khi gọi tool; thiếu handle/URL thì gọi `clarify` hỏi người dùng, không được bịa.
  - Rule: Trước khi gửi/đăng bài ra ngoài, bắt buộc gọi `clarify` dạng yes/no để xác nhận; chỉ gọi `send` với `confirmed=true` sau khi người dùng đồng ý.
- **Kết quả eval**: Đạt **0.75** (15/20 PASS). Model đã bắt đầu nhận thức được việc hỏi lại và xin xác nhận. Tuy nhiên phát sinh lỗi mới: model điền handle giả `your_twitter_account` (R10) hoặc URL giả `example.com` (R11), và ở R13 model gọi `lookup` nhưng thiếu tham số `topic=news`. Điều này chứng minh chỉ sửa system prompt là chưa đủ, cần phải sửa song song cả Tool Declaration (`tools.yaml`).

### Vòng 3 — Version v3: Đồng bộ System Prompt và Chuẩn hóa Tool Declaration
- **Vấn đề v2**: Model bị nhầm lẫn giữa tìm kiếm theo account (`timeline`) và tìm kiếm theo chủ đề (`social_search`), bịa handle/URL vì description của tool trong `tools.yaml` chưa có ranh giới cấm rõ ràng; các tham số như `topic` hay `timeframe` của `lookup` dễ bị bỏ sót hoặc truyền sai format.
- **Giả thuyết**: Cụ thể hóa routing nguồn trong system prompt kết hợp viết lại `tools.yaml` với ranh giới sử dụng rõ ràng (when to use / when not to use) và convention tham số chuẩn xác sẽ loại bỏ triệt để các lỗi routing sai và sai giá trị tham số.
- **Thay đổi**:
  - `system_prompt.md`: Làm rõ quy tắc routing nguồn: `timeline` chỉ dùng khi đã biết account; không gọi `social_search` với query rỗng; trong hội thoại nhiều lượt (multi-turn), luôn tuân theo chỉ dẫn nguồn mới nhất của người dùng; chỉ định rõ `clarify(response_type="text")` khi thiếu thông tin và `clarify(response_type="yes_no")` khi cần xác nhận.
  - `tools.yaml`: Viết lại description cho toàn bộ các tool chính:
    + `timeline`: Ghi rõ chỉ dùng khi biết account; `screenname` không chứa `@`; không dùng để tìm kiếm theo chủ đề.
    + `social_search`: Dùng tìm kiếm tweet theo keyword/chủ đề; phân biệt rõ `search_type` là `Top` hoặc `Latest`.
    + `lookup`: Quy định `query` chỉ chứa chủ đề (không nhồi thêm chữ "news"); tìm tin tức bắt buộc `topic="news"`; `timeframe` chuẩn hóa (`day`, `week`, `month`, `year`).
    + `fetch`: Cấm tự bịa URL; thiếu URL phải hỏi lại bằng `clarify`.
    + `send`: Cấm gọi khi chưa có xác nhận rõ ràng từ người dùng.
- **Kết quả eval**: Case accuracy nhảy vọt từ **0.75 lên 0.95 (19/20 PASS)**, Tool Routing đạt **1.00 (20/20)**, Argument accuracy đạt **0.95**, Multi-turn accuracy đạt **1.00**. Khắc phục triệt để các lỗi R10, R11, R13. Chỉ còn 1 case R12 chưa pass do model cẩn thận hỏi xin nội dung trước khi hỏi xác nhận gửi.
- Bản v3 này sau đó được nhóm chọn làm nền tảng cho bản tích hợp `v3-int` (giữ nguyên độ chính xác 0.95 trên base eval khi bổ sung 4 tool mới) và chuyển giao cho các thành viên chạy thử nghiệm Small Local Model.

## 4. Bằng chứng

- **Commits kỹ thuật**:
  - Commit `772e614`: `fix system-prompt and run eval version 1` — nâng độ chính xác từ 0.65 lên 0.80.
  - Commit `7db0972`: `fix system-prompt and run eval version 2` — thêm rule thiếu thông tin và xác nhận hành động (0.75).
  - Commit `65bf68f`: `fix system-prompt, tool declaration and run eval version 3` — nâng độ chính xác lên 0.95 (19/20 PASS).
- **Run JSON hợp lệ (`provider_error_cases == 0`, `measured_cases == 20`)**:
  - `starter_v0/runs/v1_B_base_openrouter_20261110T182732220052.json`
  - `starter_v0/runs/v2_B_base_openrouter_20261110T184712806825.json`
  - `starter_v0/runs/v3_B_base_openrouter_20261110T190626530147.json`
- **Nhật ký phiên bản**:
  - File `starter_v0/artifacts/version_log.csv` ghi nhận đầy đủ 3 dòng v1, v2, v3 kèm mã hash commit, giả thuyết và metric trước/sau.
- **Báo cáo nhóm**:
  - Đóng góp nội dung cho Bảng B1 (Version Evidence), Mục 3 (Giải pháp Prompt & Tools) và Mục 7 (B6. Reflection) trong `report/team/group_report.md`.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả**:
  - Sử dụng trợ lý AI để hỗ trợ rà soát cấu trúc cú pháp YAML, đối chiếu sự sai khác giữa schema declaration và prompt text.
  - Tự kiểm tra: Chạy `run_eval.py --suite base` sau mỗi lần chỉnh sửa; kiểm tra hash SHA-256 của prompt và tool declaration đảm bảo thay đổi đúng dự kiến; đọc trực tiếp log `actual_tool_calls` và `failures` trong file run JSON để xác minh nguyên nhân tăng/giảm điểm trước khi bước sang vòng lặp tiếp theo.

## 5. Tự đánh giá

- **Mức độ hoàn thành**: Hoàn thành 100% nhiệm vụ được giao ở Checkpoint CP2. Đưa độ chính xác của agent từ mức cơ bản 0.65 lên 0.95 (tăng 30% tuyệt đối, đạt 19/20 case).
- **Điểm làm tốt**:
  - Áp dụng nghiêm túc phương pháp luận khoa học: mỗi version gắn liền với một giả thuyết rõ ràng, đo lường bằng số liệu thật, không sửa bừa bãi.
  - Nhận diện đúng vai trò của Tool Declaration: không cố nhồi nhét mọi thứ vào system prompt mà chia sẻ trách nhiệm cho `tools.yaml` (ranh giới sử dụng và convention tham số).
  - Bản prompt/tools v3 có tính tổng quát cao, tương thích tốt cả khi tích hợp thêm 4 tool mới của nhóm và hỗ trợ tốt cho các thử nghiệm local model.
- **Điểm cần cải thiện**:
  - Có thể tối ưu sâu hơn ở case R12 để xử lý đồng thời cả hai tình huống: vừa hỏi xin nội dung vừa xin xác nhận gửi trong một câu hỏi để đạt điểm tuyệt đối 20/20.

