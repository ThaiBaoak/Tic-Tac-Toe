DIRS = [(0,1), (1,0), (1,1), (1,-1)]

class Board:
    def __init__(self, n=3, k=3):
        self.n, self.k = n, k
        self.grid = [[0] * n for _ in range(n)]
        self.player = 1
        self.history = []
        self.winner_ = None
        self.win_line = None

    def legal_moves(self):
        return [(r, c) for r in range(self.n) for c in range(self.n) if self.grid[r][c] == 0]

    def play(self, move):
        r, c = move
        self.grid[r][c] = self.player
        self.history.append(move)
        line = self.winning_line(r, c)
        if line:
            self.winner_, self.win_line = self.player, line
        self.player = 3 - self.player

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

    def is_full(self):
        return len(self.history) == self.n * self.n

    def is_terminal(self):
        return self.winner_ is not None or self.is_full()

    def undo(self):
        r, c = self.history.pop()
        self.grid[r][c] = 0
        self.player = 3 - self.player
        self.winner_, self.win_line = None, None

    @property
    def last_move(self):
        return self.history[-1] if self.history else None

    def copy(self):
        b = Board(self.n, self.k)
        b.grid = [row[:] for row in self.grid]
        b.player = self.player
        b.history = self.history[:]
        b.winner_, b.win_line = self.winner_, self.win_line
        return b

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

