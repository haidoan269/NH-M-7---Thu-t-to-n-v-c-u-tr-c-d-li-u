# Thuật toán và cấu trúc dữ liệu – Mã nguồn thí nghiệm

Mã nguồn đi kèm **Báo cáo bài tập lớn học phần Nhập môn về kỹ thuật (IT6217)**,
đề tài: *Trình bày về thuật toán và cấu trúc dữ liệu liên quan đến ngành Khoa học máy tính*.

- Trường: Công nghệ thông tin và Truyền thông – Đại học Công nghiệp Hà Nội
- Nhóm 7 – Lớp học phần 2026DHKHMT02 – Khóa K21
- Giảng viên hướng dẫn: Nhữ Văn Kiên
- Thành viên: Đoàn Minh Hải (nhóm trưởng), Nguyễn Việt Hải, Phạm Thanh Hải, Bùi Công Hiếu, Nguyễn Hoàng Hiệp

## Yêu cầu
Python 3 (chỉ dùng thư viện chuẩn, không cần cài thêm gói).

## Cấu trúc thư mục
| Tệp | Mô tả |
|---|---|
| `bench.py` | Khung đo hiệu năng dùng chung (đồng hồ, lặp lại, bộ nhớ, đếm thao tác) |
| `sorting.py` | 5 biến thể thuật toán sắp xếp (kèm bản đếm so sánh) |
| `structures.py` | 4 cấu trúc dữ liệu: mảng, danh sách liên kết, bảng băm, BST |
| `exp1_sorting.py` | Thí nghiệm 1 (mục 3.2): so sánh thuật toán sắp xếp |
| `exp2_search.py` | Thí nghiệm 2 (mục 3.3): so sánh cấu trúc dữ liệu cho bài toán tìm kiếm |
| `demo_autocomplete.py` | Minh họa gợi ý từ khóa (mục 3.4.2) |
| `exp3_sqlite.py` | Minh họa chỉ mục cơ sở dữ liệu SQLite (mục 3.4.3) |
| `results/` | Kết quả đo (CSV/JSON) sinh ra khi chạy các chương trình |

## Cách chạy
```bash
python sorting.py            # kiểm tra tính đúng đắn các thuật toán sắp xếp
python structures.py         # kiểm tra tính đúng đắn các cấu trúc dữ liệu
python exp1_sorting.py       # Thí nghiệm 1 (khoảng 6 phút)
python exp2_search.py        # Thí nghiệm 2 (khoảng 2 phút)
python demo_autocomplete.py  # minh họa gợi ý từ khóa
python exp3_sqlite.py        # minh họa chỉ mục cơ sở dữ liệu
```
Các thí nghiệm dùng seed cố định nên có thể chạy lại để đối chiếu kết quả; thời gian đo cụ thể phụ thuộc cấu hình máy.
