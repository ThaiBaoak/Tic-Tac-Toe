from .base import Agent

INF = float("inf")
WIN = 10 ** 9
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1))

class AlphaBetaAgent(Agent):
    name = "Alpha-beta"

    def __init__(self, depth=3):
        super().__init__()
        self.depth = depth
        self.board = None
        self.nodes = 0

    def choose_move(self, board, time_limit=None):
        self.board = board
        self.nodes = 0
        r, c, _ = self.alpha_beta_pruning(self.depth, -INF, INF, board.player)
        if r == -1:
            r, c = board.candidate_moves()[0]
        self.stats = {"nodes": self.nodes, "depth": self.depth}
        return (r, c)

    def alpha_beta_pruning(self, depth, alpha, beta, player):
        self.nodes += 1
        r = -1
        c = -1
        if depth == 0 or self.board.is_terminal():
            return [r,c,self.get_score()]
        else:
            for cell in self.board.candidate_moves():
                self.board.play(cell)
                score = self.alpha_beta_pruning(depth-1, alpha, beta, 3-player)

                if (player==1):
                    if(score[2]>alpha):
                        alpha= score[2]
                        r=cell[0]
                        c=cell[1]
                else:
                    if score[2]<beta:
                        beta = score[2]
                        r = cell[0]
                        c = cell[1]

                self.board.undo()

                if(alpha >= beta):
                    break
        if(player==1):
            return [r,c,alpha]
        else:
            return [r,c,beta]

    def get_score(self):
        b = self.board
        if b.winner_ == 1:
            return WIN +  self.depth
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
            

    