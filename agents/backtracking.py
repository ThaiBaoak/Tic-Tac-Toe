from .evaluation import INF, SearchAgent


# Minimax giới hạn độ sâu, không cắt tỉa
class BacktrackingAgent(SearchAgent):
    name = "Backtracking"

    def choose_move(self, board, time_limit=None):
        if board.is_terminal():
            return None
        self.attach(board.copy())
        player = self.board.player
        r, c, _ = self.backtracking(self.depth, player, ordered=True)
        if r == -1:
            r, c = self.ordered_candidates(player)[0]
        self.stats = {"nodes": self.nodes, "depth": self.depth}
        return (r, c)

    def backtracking(self, depth, player, ordered=False):
        self.nodes += 1
        if depth == 0 or self.board.is_terminal():
            return [-1, -1, self.get_score(depth)]

        moves = self.ordered_candidates(player) if ordered else self.candidates()
        if not moves:
            return [-1, -1, self.get_score(depth)]

        r = c = -1
        best_score = -INF if player == 1 else INF
        for cell in moves:
            self.do(cell)
            score = self.backtracking(depth - 1, 3 - player)[2]
            self.undo()

            if player == 1:
                if score > best_score:
                    best_score, r, c = score, cell[0], cell[1]
            else:
                if score < best_score:
                    best_score, r, c = score, cell[0], cell[1]

        return [r, c, best_score]
