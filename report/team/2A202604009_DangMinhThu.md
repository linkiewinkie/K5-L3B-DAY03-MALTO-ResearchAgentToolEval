# Báo cáo cá nhân — Đặng Minh Thu-2A202604009


## 1. Thông tin thành viên

- Họ tên: Đặng Minh Thu
- MSSV: 2A202604009
- Email: 26ai.thudm@vinuni.edu.vn

## 2. Phần việc phụ trách

Custom Tool + Unit Testing (CP3), branch `minhthu`. Phụ trách bonus "hơn 3 tool mới"
và "test challenge".

## 3. Đóng góp cụ thể

- Viết 4 tool mới: dedupe, filter_results, topic_stats, reading_list (tool.py, TOOL.md,
  đăng ký trong tools/__init__.py, khai báo trong artifacts/tools.yaml).
- Viết 33 unit test cho 4 tool mới (happy path / input xấu / nhánh lỗi), offline.
- Điền 14 stub test TODO của 8 tool có sẵn → pytest 138 passed, 0 skipped.
- Tìm và sửa 2 bug ở tool có sẵn (limit âm trong timeline/social_search; format crash khi
  item không phải dict), kèm test regression.
- Gửi contract 4 tool cho nhóm trưởng để viết eval case.

## 4. Bằng chứng

- File/commit/PR:
  - **Tool mới** (mỗi tool có `tool.py` + `TOOL.md`): `starter_v0/tools/dedupe/`, `starter_v0/tools/filter_results/`, `starter_v0/tools/topic_stats/`, `starter_v0/tools/reading_list/`
  - **Đăng ký / khai báo:** `starter_v0/tools/__init__.py` (`TOOL_FUNCTIONS`), `starter_v0/artifacts/tools.yaml`
  - **Unit test:** `starter_v0/tests/test_tools_todo.py` (33 test cho 4 tool mới, 14 stub TODO đã điền, 3 test regression)
  - **Sửa bug tool có sẵn:** `starter_v0/tools/timeline/tool.py`, `starter_v0/tools/social_search/tool.py`, `starter_v0/tools/format/tool.py`
  - **Commit (branch `minhthu`):**
    - `83d6d81` Add dedupe tool with 7 unit tests (CP3)
    - `206140f` Replace rank/extract_links/summarize_stats with filter_results, topic_stats, reading_list
    - `47c07d7` Fill TODO tests, fix timeline/social_search/format bugs + regression tests
  - **Kết quả pytest:** `python -m pytest -q` → 138 passed, 0 skipped, 0 failed; `pytest tests/test_tool_contract.py` → 75 passed

- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Sử dụng Claude Code như công cụ hỗ trợ viết unit test, rà soát code và phát hiện các trường hợp lỗi tiềm ẩn. Các đề xuất từ AI đều được tôi xem xét, đối chiếu và kiểm tra lại trước khi chấp nhận; việc đánh giá và xác nhận kết quả cuối cùng do tôi thực hiện.
  - Với 2 bug được phát hiện, tôi đưa các bản sửa trong `tools/` ra ngoài để kiểm chứng: xác nhận 3 regression test **fail** trên code cũ (`AttributeError` ở `format`, mất tweet cuối ở `timeline`/`social_search`) và **pass** sau khi áp dụng bản sửa, đảm bảo test thực sự phát hiện được lỗi.
  - Test chạy offline: `block_network` chặn các yêu cầu mạng thật, HTTP được mock bằng `fake_http`.

## 5. Tự đánh giá

**Làm tốt**

- Bốn tool mới giải quyết các nhu cầu còn thiếu sau khi tìm kiếm: làm sạch, lọc, thống kê và lưu kết quả.

| Tool | Giá trị thực tế | Starter thiếu gì |
|---|---|---|
| `dedupe` | Loại bài trùng khi tổng hợp từ nhiều nguồn. | `format` chỉ định dạng, không loại trùng. |
| `filter_results` | Lọc kết quả đã có theo nguồn và thời gian mà không cần gọi lại API. | `lookup` chưa hỗ trợ lọc kết quả đã trả về theo nguồn. |
| `topic_stats` | Thống kê số lượng, tỉ lệ và nguồn theo chủ đề. | Chưa có công cụ thống kê trên nhiều bài. |
| `reading_list` | Lưu, xem lại và xoá bài viết qua nhiều lượt chat. | Chưa có cơ chế lưu bài đọc sau. |

- Các tool có thể kết hợp thành quy trình `lookup` → `dedupe` → `filter_results` → `topic_stats` → `format`; `reading_list` hỗ trợ lưu lại những bài được chọn.
- Hoàn thiện đầy đủ cấu trúc và contract cho 4 tool; viết 33 unit test, điền 14 stub TODO và sửa 2 bug ở tool có sẵn. Kết quả kiểm thử đạt 138 passed, 0 skipped, 0 failed.
- Các lỗi được kiểm chứng bằng regression test: test fail trên code cũ và pass sau khi sửa.

**Hướng cải thiện tiếp theo**

- Nâng cấp `dedupe` để nhận diện nội dung trùng lặp dù khác URL hoặc tiêu đề.
- Cải thiện `topic_stats` bằng cách nhóm các từ khoá gần nghĩa.
- Kiểm thử thêm với dữ liệu thực từ `lookup` và `social_search`.

**Bài học**

- Unit test không chỉ kiểm tra luồng chạy bình thường mà còn cần bao phủ input biên và dữ liệu không đúng định dạng.
- Tool nên xử lý lỗi có kiểm soát và trả về thông báo phù hợp để không làm gián đoạn vòng lặp agent.
- Với tool có tác dụng phụ như `reading_list`, các thao tác nguy hiểm cần được kiểm soát ngay trong code, không chỉ dựa vào mô tả.
- Cần đọc test mẫu và fixture có sẵn trước khi triển khai để tận dụng cơ chế kiểm thử ổn định, tránh phụ thuộc API thật.