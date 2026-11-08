from .base import Agent

INF = float("inf")
WIN = 10 ** 9
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1))

class BacktrackingAgent(Agent):
    name = "Backtracking"

    def __init__(self, depth=3):
        super().__init__()
        self.depth = depth
        self.board = None
        self.nodes = 0

    def choose_move(self, board, time_limit=None):
        self.board = board
        self.nodes = 0
        r, c, _ = self.backtracking(self.depth, board.player)
        if r == -1:
            r, c = board.candidate_moves()[0]
        self.stats = {"nodes": self.nodes, "depth": self.depth}
        return (r, c)

    def backtracking(self, depth, player):
        self.nodes += 1
        r = -1
        c = -1
        if (depth == 0 or self.board.is_terminal()):
            return [r, c, self.get_score()]
        else:
            best_score = -INF if player == 1 else INF

            for cell in self.board.candidate_moves():
                self.board.play(cell)
                score = self.backtracking(depth - 1, 3 - player)

                if (player == 1):
                    if (score[2] > best_score):
                        best_score = score[2]
                        r = cell[0]
                        c = cell[1]
                else:
                    if (score[2] < best_score):
                        best_score = score[2]
                        r = cell[0]
                        c = cell[1]

                self.board.undo()

        return [r, c, best_score]

    def get_score(self):
        b = self.board
        if b.winner_ == 1:
            return WIN + self.depth
        if b.winner_ == 2:
            return -WIN - self.depth
        return self._lines_score(1) - self._lines_score(2)

    def _lines_score(self, p):
        b = self.board
        n, k = b.n, b.k
        total = 0
        grid = b.grid

        for r in range(n):
            for c in range(n):
                for dr, dc in DIRS:
                    # Kiểm tra ô có nằm trong bàn cờ
                    er, ec = r + (k - 1) * dr, c + (k - 1) * dc
                    if not (0 <= er < n and 0 <= ec < n):
                        continue

                    mine = 0
                    blocked = False

                    for i in range(k):
                        v = grid[r + i * dr][c + i * dc]
                        if v == p:
                            mine += 1
                        elif v != 0:  # Bị chặn
                            blocked = True
                            break

                    # Tính điểm
                    if not blocked and mine > 0:
                        score = 10 ** mine
                        total += score

        return total
