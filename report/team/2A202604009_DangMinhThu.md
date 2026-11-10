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
- Bốn tool mới cùng giải một bài toán: sau khi `lookup`/`social_search` trả về danh sách kết quả thô, người dùng cần làm sạch, lọc, phân tích và lưu lại. Starter chưa có tool nào làm các bước này.

  | Tool | Giá trị thực tế | Starter thiếu gì |
  |---|---|---|
  | `dedupe` | Khi gộp nhiều nguồn, cùng một bài hay xuất hiện nhiều lần. Tool loại trùng theo URL (bỏ `www`, `/` cuối, không phân biệt hoa thường) hoặc theo tiêu đề, trước khi `format` ra bản tin. | `format` chỉ định dạng, không loại trùng. |
  | `filter_results` | Người dùng thường yêu cầu "chỉ lấy tin từ Reuters" hoặc "trong 7 ngày gần đây". Tool lọc danh sách đã có theo nguồn và theo ngày, không cần gọi lại API. | `lookup` chỉ có `timeframe` khi tìm, không lọc được kết quả đã có theo nguồn. |
  | `topic_stats` | Thay vì đọc từng bài, người dùng hỏi "chủ đề nào được nhắc nhiều nhất". Tool trả số bài, tỉ lệ, nguồn tiêu biểu cho mỗi chủ đề, hoặc đếm đúng các chủ đề người dùng nêu. | Không có tool nào tổng hợp thống kê trên nhiều bài. |
  | `reading_list` | Lưu bài "đọc sau", xem lại và xoá, bền qua nhiều lượt chat (file JSON local). Đây là tool duy nhất có tác dụng phụ ghi file, nên `clear` bắt buộc `confirmed=true`. | Starter không có bộ nhớ lưu bài cho người dùng. |

- Bốn tool nối thành một chuỗi: `lookup` → `dedupe` → `filter_results` → `topic_stats` → `format`, còn `reading_list` lưu lại bài người dùng chọn. Mỗi tool có thể dùng độc lập.
- Mỗi tool có `tool.py`, `TOOL.md`, đăng ký trong `TOOL_FUNCTIONS`, khai báo trong `tools.yaml`. `test_tool_contract.py` xanh (75 passed), nên tên và tham số khớp giữa các lớp.
- Test đủ ba loại theo yêu cầu CP3: happy path, input xấu từ model (`None`, sai kiểu, `limit` dạng chuỗi), và nhánh lỗi. Tổng 33 test cho 4 tool (8–9 test/tool), chạy offline.
- Tool trả error dict thay vì raise, và `reading_list` không ghi đè file JSON bị hỏng.
- Điền xong 14 stub TODO; `pytest` đạt 138 passed, 0 skipped, 0 failed.
- Tìm 2 bug trong tool có sẵn (`limit` âm trong `timeline`/`social_search` làm mất tweet cuối; `format` crash khi item không phải dict), đã sửa và có test regression. Các test này fail trên code cũ và pass sau khi sửa.

**Hạn chế**
- `dedupe` chỉ so khớp theo URL hoặc tiêu đề đã chuẩn hoá, nên không nhận ra hai bài cùng nội dung nhưng khác URL và khác tiêu đề.
- `topic_stats` đếm theo từ khoá (mỗi bài một phiếu), không hiểu ngữ nghĩa. Hai cách diễn đạt khác nhau của cùng một chủ đề có thể bị tách thành hai chủ đề.
- `filter_results` loại item không có ngày hợp lệ khi đặt `days`. Hành vi này có chủ ý nhưng nếu nguồn không trả ngày thì kết quả có thể ít hơn người dùng mong đợi.
- `reading_list` lưu file local cho một người dùng; chưa xử lý nhiều tiến trình ghi cùng lúc và chưa có test cho trường hợp này.
- Bộ test chỉ kiểm tra bằng dữ liệu giả lập; chưa kiểm tra với kết quả thật từ `lookup`/`social_search`.
- Với `timeline` và `social_search`, tôi mới xử lý `limit` âm; các giá trị biên khác (`limit=0` quay về mặc định 5, `top_k`, `max_results` âm) chưa được đánh giá là đúng hay sai, nên chưa có test.

**Bài học**
- Unit test đo code của tool có chạy đúng không. Nhiều lỗi chỉ lộ ra khi gửi input biên mà model hay gửi, như `limit` âm, số dạng chuỗi, hoặc phần tử không phải dict trong danh sách.
- Tool nên trả error dict thay vì raise, để lỗi không thoát ra vòng lặp agent. Hai bug tìm được ở tool có sẵn đều thuộc nhóm lỗi này.
- Với tool có tác dụng phụ (`reading_list`), phần nguy hiểm (`clear`) phải được chặn ngay trong code bằng `confirmed`, chứ không chỉ dựa vào mô tả.
- Nên đọc test mẫu (`test_tools_examples.py`) và `conftest.py` trước khi viết test, vì các fixture `fake_http` và `block_network` giúp test nhanh, ổn định và không tốn API.
