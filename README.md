# Tic-Tac-Toe n×n (k quân liên tiếp)

**Homework 2 – Nhập môn Trí tuệ Nhân tạo (CO3061)**
Trường ĐH Bách Khoa – ĐHQG-HCM · GVHD: TS. Nguyễn Quốc Minh
Topic 1: Tic-tac-toe trên bàn lớn (7×7, 9×9, 11×11, …) với Backtracking, Alpha-beta pruning, MCTS và so sánh các phương pháp.

## Thành viên

| STT | Họ và tên | MSSV | Nhiệm vụ chính | Đóng góp |
|---|---|---|---|---|
| 1 | Trần Đức Hiếu | 2452335 | Cài đặt thuật toán MCTS  | 100% |
| 2 | Trần Ngọc Phương Mai | 2452720| Thiết kế và cài đặt giao diện (GUI) | 100% |
| 3 | Thái Lê Gia Bảo | 2452142 | Cài đặt thuật toán Alpha-beta pruning | 100% |
| 4 | Nguyễn Gia Bảo | 2452127 | Cài đặt thuật toán Backtracking | 100% |

## Giới thiệu

Chương trình mô phỏng trò chơi tic-tac-toe tổng quát trên bàn **n×n**, người chơi nào có **k quân liên tiếp** (ngang, dọc, chéo) trước thì thắng. Người dùng có thể chơi với máy hoặc cho các thuật toán đấu với nhau trên giao diện đồ họa, đồng thời so sánh hiệu quả của từng thuật toán.

## Luật chơi

- Bàn cờ n×n, hai người chơi X (đi trước) và O thay phiên đặt quân vào ô trống.
- Thắng khi có ít nhất **k quân liên tiếp** của mình theo hàng ngang, hàng dọc hoặc đường chéo.
- Bàn đầy mà không ai thắng thì **hòa**.
- Cấu hình gợi ý: 3×3 với k=3 (để kiểm chứng, giải được hoàn toàn), 7×7 với k=4 hoặc 5, 9×9 và 11×11 với k=5.

## Cấu trúc thư mục

```
Tic-Tac-Toe/
├── main.py                 # điểm khởi chạy GUI
├── requirement.txt
├── README.md
├── game/
│   └── board.py            # lớp Board: luật chơi, trạng thái
├── agents/
│   ├── __init__.py         # đăng ký các agent (AGENTS)
│   ├── base.py             # lớp Agent (interface chung)
│   ├── random_agent.py     # agent ngẫu nhiên (mốc so sánh)
│   ├── backtracking.py     # Backtracking
│   ├── alphabeta.py        # Alpha-beta pruning
│   └── mcts.py             # MCTS (cập nhật khi hoàn thành)
├── gui/
│   └── app.py              # giao diện Tkinter
```

Các thư mục đều có `__init__.py` (có thể rỗng) để import theo gói.

## Cài đặt và chạy

Yêu cầu: **Python 3.9 trở lên**. Giao diện dùng `tkinter` (có sẵn khi cài Python; trên Linux cài thêm bằng `sudo apt install python3-tk`).

```bash
pip install -r requirement.txt
```

Chạy giao diện **từ thư mục gốc của dự án**:

```bash
python main.py
```

(Hoặc `python -m gui.app`. Không chạy trực tiếp `python gui/app.py`, vì Python sẽ không tìm thấy các gói `game` và `agents`.)

## Sử dụng giao diện

- Chọn **n** (kích thước bàn) và **k** (số quân thắng) rồi bấm **Ván mới**.
- Chọn loại người chơi cho X và O: **Human** hoặc một trong các agent (Random, Backtracking, Alpha-beta, …).
- Bấm vào ô trống để đi khi đến lượt người chơi. Có thể chọn máy đấu với máy.
- **Hoàn tác** để lùi nước đi gần nhất.
- Các ô tạo thành đường thắng được tô màu; bàn đầy mà chưa ai thắng thì báo hòa.

## Các thuật toán

| Thuật toán | File | Ý tưởng |
|---|---|---|
| Random | `agents/random_agent.py` | Chọn ngẫu nhiên một ô trống, dùng làm mốc so sánh |
| Backtracking | `agents/backtracking.py` | Duyệt cây trò chơi (minimax không cắt tỉa) đến độ sâu giới hạn, dùng hàm đánh giá ở nút lá |
| Alpha-beta | `agents/alphabeta.py` | Minimax có cắt tỉa alpha-beta, cho cùng kết quả như backtracking nhưng duyệt ít nút hơn |
| MCTS | `agents/mcts.py` | Monte Carlo Tree Search (UCT): selection, expansion, simulation, backpropagation |

Quy ước chung:

- Chỉ xét các ô trống **gần quân đã đặt** (`board.candidate_moves()`) để giảm số nhánh ở bàn lớn.
- Hàm đánh giá tính theo **góc nhìn của X**: điểm dương có lợi cho X, điểm âm có lợi cho O. X là bên cực đại, O là bên cực tiểu.
- Thắng cho điểm rất lớn (`WIN`), còn lại tính theo số quân liên tiếp chưa bị chặn trong mỗi đoạn dài k ô.

