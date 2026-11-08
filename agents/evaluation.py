import time

from .base import Agent

INF = float("inf")
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1))

_WINDOW_CACHE = {}


# Với mỗi ô, trả về danh sách các cửa sổ k ô liên tiếp chứa ô đó
def build_windows(n, k):
    if (n, k) not in _WINDOW_CACHE:
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
        _WINDOW_CACHE[(n, k)] = (cell_windows, count)
    return _WINDOW_CACHE[(n, k)]


# Điểm đánh giá, cập nhật dần mỗi khi đặt hoặc gỡ một quân
# Cửa sổ chỉ có quân một bên: 10^số_quân, có quân cả hai bên: 0
class LineEvaluator:
    def __init__(self, n, k):
        self.n, self.k = n, k
        self.cell_windows, self.num_windows = build_windows(n, k)
        self.weight = [0] + [10 ** m for m in range(1, k + 1)]
        self.win = 10 ** (k + 3)
        self.threat_score = self.win // 2
        self.reset()

    def reset(self, grid=None):
        self.count = [None, [0] * self.num_windows, [0] * self.num_windows]
        self.score = [0, 0, 0]
        self.threats = [0, 0, 0]    # số cửa sổ còn thiếu đúng 1 quân là thắng
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
            if b == 0:
                score[p] += w[a + 1] - w[a]
                if a == km1:
                    threats[p] -= 1
                elif a + 1 == km1:
                    threats[p] += 1
            elif a == 0:
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
            elif a == 1:
                score[o] += w[b]
                if b == km1:
                    threats[o] += 1
            mine[wid] = a - 1

    # Giá trị của việc đặt quân p vào ô (r, c), dùng để sắp xếp nước đi
    def cell_value(self, r, c, p):
        mine, theirs, w = self.count[p], self.count[3 - p], self.weight
        total = 0
        for wid in self.cell_windows[r * self.n + c]:
            if theirs[wid] == 0:
                total += w[mine[wid] + 1]
        return total


class SearchTimeout(Exception):
    pass


# Phần chung của Backtracking và Alpha-beta
class SearchAgent(Agent):
    SMALL_BOARD = 25    # bàn nhỏ thì xét mọi ô trống, bàn lớn chỉ xét ô kề quân đã đánh

    def __init__(self, depth=3):
        super().__init__()
        if depth < 1:
            raise ValueError("depth must be at least 1")
        self.depth = depth
        self.board = None
        self.evaluator = None
        self.nodes = 0

    def attach(self, board):
        self.board = board
        self.nodes = 0
        self.evaluator = LineEvaluator(board.n, board.k)
        self.evaluator.reset(board.grid)

    def do(self, move):
        player = self.board.player
        self.board.play(move)
        self.evaluator.place(move[0], move[1], player)

    def undo(self):
        r, c = self.board.history[-1]
        player = 3 - self.board.player
        self.board.undo()
        self.evaluator.remove(r, c, player)

    def candidates(self):
        if self.board.n * self.board.n <= self.SMALL_BOARD:
            return self.board.legal_moves()
        return self.board.candidate_moves()

    # Sắp xếp nước đi: nước vừa tấn công vừa chặn đối thủ được xét trước
    def ordered_candidates(self, player):
        ev = self.evaluator
        moves = self.candidates()
        moves.sort(key=lambda m: -(ev.cell_value(m[0], m[1], player) + ev.cell_value(m[0], m[1], 3 - player)))
        return moves

    # Điểm theo góc nhìn của X: dương là X lợi, âm là O lợi
    # depth là độ sâu còn lại, thắng càng sớm thì điểm càng cao
    def get_score(self, depth=0):
        board, ev = self.board, self.evaluator
        if board.winner_ is not None:
            value = ev.win + depth
            return value if board.winner_ == 1 else -value
        if board.is_full():
            return 0
        mover = board.player
        if ev.threats[mover]:
            return ev.threat_score if mover == 1 else -ev.threat_score
        return ev.score[1] - ev.score[2]
