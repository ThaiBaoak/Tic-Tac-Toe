import time

from .evaluation import INF, SearchAgent, SearchTimeout


class AlphaBetaAgent(SearchAgent):
    name = "Alpha-beta"

    def __init__(self, depth=3):
        super().__init__(depth)
        self.deadline = None
        self.root_len = 0
        self.pv_move = None

    def choose_move(self, board, time_limit=None):
        if board.is_terminal():
            return None
        self.attach(board.copy())
        self.root_len = len(self.board.history)
        self.pv_move = None
        player = self.board.player

        if time_limit is None:
            self.deadline = None
            r, c, _ = self.alpha_beta_pruning(self.depth, -INF, INF, player)
            reached = self.depth
        else:
            r, c, reached = self.iterative_deepening(player, time.perf_counter() + time_limit)

        if r == -1:
            r, c = self.ordered_candidates(player)[0]
        self.stats = {"nodes": self.nodes, "depth": reached}
        return (r, c)

    # Tăng dần độ sâu tới khi hết giờ, lấy nước của độ sâu cuối cùng duyệt xong
    def iterative_deepening(self, player, deadline):
        best = (-1, -1)
        reached = 0
        max_depth = self.board.n * self.board.n - self.root_len
        for depth in range(1, max_depth + 1):
            self.deadline = deadline if depth > 1 else None
            try:
                r, c, value = self.alpha_beta_pruning(depth, -INF, INF, player)
            except SearchTimeout:
                break
            if r != -1:
                best = (r, c)
                self.pv_move = best
            reached = depth
            if abs(value) >= self.evaluator.win or time.perf_counter() >= deadline:
                break
        return best[0], best[1], reached

    def alpha_beta_pruning(self, depth, alpha, beta, player):
        self.nodes += 1
        if self.deadline is not None and self.nodes % 512 == 0 and time.perf_counter() > self.deadline:
            raise SearchTimeout()

        if depth == 0 or self.board.is_terminal():
            return [-1, -1, self.get_score(depth)]

        moves = self.ordered_candidates(player)
        if len(self.board.history) == self.root_len and self.pv_move in moves:
            moves.remove(self.pv_move)
            moves.insert(0, self.pv_move)
        if not moves:
            return [-1, -1, self.get_score(depth)]

        r = c = -1
        for cell in moves:
            self.do(cell)
            score = self.alpha_beta_pruning(depth - 1, alpha, beta, 3 - player)[2]
            self.undo()

            if player == 1:
                if score > alpha:
                    alpha, r, c = score, cell[0], cell[1]
            else:
                if score < beta:
                    beta, r, c = score, cell[0], cell[1]

            if alpha >= beta:
                break

        return [r, c, alpha if player == 1 else beta]
