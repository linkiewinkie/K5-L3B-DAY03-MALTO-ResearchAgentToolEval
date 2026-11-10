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
|   3 | <Họ tên Lên> | <MSSV> | <email> | <github> | Prompt Engineering + tối ưu v1–v3 |
|   4 | <Họ tên Thu> | <MSSV> | <email> | <github> | Custom Tool + Unit Testing |

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

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## <HoVaTen>-<MSSV> (Lên)

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## <HoVaTen>-<MSSV> (Thu)

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
