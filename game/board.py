DIRS = [(0,1), (1,0), (1,1), (1,-1)]

class Board:
    #Tạo ván mới
    def __init__(self, n=3, k=3):
        self.n, self.k = n, k
        self.grid = [[0] * n for _ in range(n)]
        self.player = 1
        self.history = []
        self.winner_ = None
        self.win_line = None

    #Trả về danh sách mọi ô còn trống
    def legal_moves(self):
        return [(r, c) for r in range(self.n) for c in range(self.n) if self.grid[r][c] == 0]

    #Đi một nước
    def play(self, move):
        r, c = move
        self.grid[r][c] = self.player
        self.history.append(move)
        line = self.winning_line(r, c)
        if line:
            self.winner_, self.win_line = self.player, line
        self.player = 3 - self.player

    #Kiểm tra xem có thắng không
    def winning_line(self, r, c):
        p = self.grid[r][c]
        for dr, dc in DIRS:
            cells = [(r, c)]
            for sign in (1, -1):
                rr, cc = r + sign * dr, c + sign * dc
                while 0 <= rr < self.n and 0 <= cc < self.n and self.grid[rr][cc] == p:
                    cells.append((rr, cc))
                    rr += sign * dr
                    cc += sign * dc
            if len(cells) >= self.k:
                return cells
        return None

    #Bàn cờ đầy
    def is_full(self):
        return len(self.history) == self.n * self.n

    #Ván kết thúc khi có người thắng hoặc bàn cờ đầy (hòa)
    def is_terminal(self):
        return self.winner_ is not None or self.is_full()

    #Lùi lại nước đi gần nhất, ngược với play
    def undo(self):
        r, c = self.history.pop()
        self.grid[r][c] = 0
        self.player = 3 - self.player
        self.winner_, self.win_line = None, None

    @property
    #Trả về bước vừa đi, None nếu chưa đi
    def last_move(self):
        return self.history[-1] if self.history else None

    #Tạo bản sao độc lập
    def copy(self):
        b = Board(self.n, self.k)
        b.grid = [row[:] for row in self.grid]
        b.player = self.player
        b.history = self.history[:]
        b.winner_, b.win_line = self.winner_, self.win_line
        return b

    #Chọn các ô trống gần ô đã đặt để giảm số nhánh tính toán
    def candidate_moves(self, dist=1):
        if not self.history:
            return [(self.n // 2, self.n // 2)]
        cand = set()
        for r, c in self.history:
            for dr in range(-dist, dist + 1):
                for dc in range(-dist, dist + 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < self.n and 0 <= cc < self.n and self.grid[rr][cc] == 0:
                        cand.add((rr, cc))
        return list(cand)

