"""Hàm đánh giá + khung tìm kiếm dùng chung cho Backtracking và Alpha-beta.

Hai agent này phải dùng CÙNG một hàm đánh giá để so sánh công bằng: alpha-beta chỉ được
phép nhanh hơn (cắt tỉa), không được cho giá trị khác backtracking ở cùng độ sâu.

Ý tưởng hàm đánh giá: chia bàn cờ thành mọi "cửa sổ" k ô liên tiếp (4 hướng). Cửa sổ chỉ
có quân của một bên thì có giá trị 10**số_quân của bên đó; cửa sổ có quân cả hai bên thì
vô giá trị. Điểm = (tổng của X) - (tổng của O). Thay vì quét lại cả bàn mỗi lần (O(n²·k)),
LineEvaluator cập nhật gia tăng khi đặt/gỡ một quân: chỉ đụng tới ≤ 4k cửa sổ chứa ô đó.
"""
import time

from .base import Agent

INF = float("inf")
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1))

_WINDOW_CACHE = {}


def _build_windows(n, k):
    """Với mỗi ô, danh sách id các cửa sổ k ô liên tiếp chứa ô đó (tính một lần cho mỗi (n, k))."""
    key = (n, k)
    if key not in _WINDOW_CACHE:
        cell_windows = [[] for _ in range(n * n)]
        count = 0
        for r in range(n):
            for c in range(n):
                for dr, dc in DIRS:
                    er, ec = r + (k - 1) * dr, c + (k - 1) * dc
                    if not (0 <= er < n and 0 <= ec < n):
                        continue
                    for i in range(k):
                        cell_windows[(r + i * dr) * n + (c + i * dc)].append(count)
                    count += 1
        _WINDOW_CACHE[key] = (cell_windows, count)
    return _WINDOW_CACHE[key]


class LineEvaluator:
    """Điểm đánh giá được cập nhật gia tăng qua place()/remove()."""

    def __init__(self, n, k):
        self.n, self.k = n, k
        self.cell_windows, self.num_windows = _build_windows(n, k)
        self.weight = [0] + [10 ** m for m in range(1, k + 1)]   # cửa sổ chưa có quân nào = 0 điểm
        # Tổng các cửa sổ <= 4n² * 10**(k-1) < 10**(k+3), nên WIN luôn lớn hơn mọi điểm heuristic.
        self.win = 10 ** (k + 3)
        self.threat_score = self.win // 2   # bên đi tiếp có k-1 quân thẳng hàng + 1 ô trống = thắng ngay
        self.reset()

    def reset(self, grid=None):
        self.count = [None, [0] * self.num_windows, [0] * self.num_windows]
        self.score = [0, 0, 0]      # score[p]: tổng giá trị các cửa sổ còn "sống" của người p
        self.threats = [0, 0, 0]    # threats[p]: số cửa sổ của p còn thiếu đúng 1 quân để thắng
        if grid:
            for r in range(self.n):
                for c in range(self.n):
                    if grid[r][c]:
                        self.place(r, c, grid[r][c])

    def place(self, r, c, p):
        o = 3 - p
        mine, theirs = self.count[p], self.count[o]
        w, km1, score, threats = self.weight, self.k - 1, self.score, self.threats
        for wid in self.cell_windows[r * self.n + c]:
            a, b = mine[wid], theirs[wid]
            if b == 0:                      # cửa sổ vẫn thuộc về p, có thêm một quân
                score[p] += w[a + 1] - w[a]
                if a == km1:
                    threats[p] -= 1
                elif a + 1 == km1:
                    threats[p] += 1
            elif a == 0:                    # cửa sổ của đối thủ bị p chặn
                score[o] -= w[b]
                if b == km1:
                    threats[o] -= 1
            mine[wid] = a + 1

    def remove(self, r, c, p):
        o = 3 - p
        mine, theirs = self.count[p], self.count[o]
        w, km1, score, threats = self.weight, self.k - 1, self.score, self.threats
        for wid in self.cell_windows[r * self.n + c]:
            a, b = mine[wid], theirs[wid]
            if b == 0:
                score[p] += w[a - 1] - w[a]
                if a == km1 + 1:
                    threats[p] += 1
                elif a == km1:
                    threats[p] -= 1
            elif a == 1:                    # gỡ quân cuối: cửa sổ của đối thủ sống lại
                score[o] += w[b]
                if b == km1:
                    threats[o] += 1
            mine[wid] = a - 1

    def cell_value(self, r, c, p):
        """Đặt quân p vào (r, c) thì "góp" được bao nhiêu vào các cửa sổ còn mở của p. Dùng để sắp thứ tự nước đi."""
        mine, theirs, w = self.count[p], self.count[3 - p], self.weight
        total = 0
        for wid in self.cell_windows[r * self.n + c]:
            if theirs[wid] == 0:
                total += w[mine[wid] + 1]
        return total


class SearchAgent(Agent):
    """Phần chung của Backtracking và Alpha-beta: duyệt cây bằng play/undo trên một bàn cờ duy nhất."""

    SMALL_BOARD = 25    # bàn <= 5x5: xét mọi ô trống; lớn hơn: chỉ xét ô kề quân đã đánh

    def __init__(self, depth=3):
        super().__init__()
        if depth < 1:
            raise ValueError("depth must be at least 1")
        self.depth = depth
        self.board = None
        self.evaluator = None
        self.nodes = 0

    def attach(self, board):
        """Gắn bàn cờ (đã được copy) và dựng lại bộ đánh giá theo thế cờ hiện tại."""
        self.board = board
        self.nodes = 0
        self.evaluator = LineEvaluator(board.n, board.k)
        self.evaluator.reset(board.grid)

    def do(self, move):
        player = self.board.player
        self.board.play(move)
        self.evaluator.place(move[0], move[1], player)

    def undo(self):
        board = self.board
        r, c = board.history[-1]
        player = 3 - board.player
        board.undo()
        self.evaluator.remove(r, c, player)

    def candidates(self):
        board = self.board
        if board.n * board.n <= self.SMALL_BOARD:
            return board.legal_moves()
        return board.candidate_moves()

    def ordered_candidates(self, player):
        """Nước đi theo thứ tự "hứa hẹn" trước: vừa tấn công (nối quân mình) vừa phòng thủ (chặn đối thủ).
        Chỉ đổi thứ tự duyệt nên không đổi giá trị minimax, nhưng giúp cắt tỉa sớm và chọn nước hòa tốt hơn."""
        ev = self.evaluator
        opponent = 3 - player
        moves = self.candidates()
        moves.sort(key=lambda m: -(ev.cell_value(m[0], m[1], player) + ev.cell_value(m[0], m[1], opponent)))
        return moves

    def get_score(self, depth=0):
        """Điểm từ góc nhìn của X (người 1): dương = X lợi, âm = O lợi.
        `depth` là độ sâu còn lại: thắng càng sớm / thua càng muộn thì điểm càng tốt."""
        board, ev = self.board, self.evaluator
        if board.winner_ is not None:
            value = ev.win + depth
            return value if board.winner_ == 1 else -value
        if board.is_full():
            return 0
        mover = board.player
        if ev.threats[mover]:               # bên đi tiếp thắng ngay được, dù đã hết độ sâu
            return ev.threat_score if mover == 1 else -ev.threat_score
        return ev.score[1] - ev.score[2]


class SearchTimeout(Exception):
    pass


def now():
    return time.perf_counter()
