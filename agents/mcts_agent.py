import math
import random
import time

from .base import Agent

DIRS = ((0, 1), (1, 0), (1, 1), (1, -1))


def completes_line(grid, n, k, r, c, player):
    """Đặt quân `player` vào ô trống (r, c) có tạo thành k quân liên tiếp không."""
    for dr, dc in DIRS:
        count = 1
        for sign in (1, -1):
            rr, cc = r + sign * dr, c + sign * dc
            while 0 <= rr < n and 0 <= cc < n and grid[rr][cc] == player:
                count += 1
                rr += sign * dr
                cc += sign * dc
        if count >= k:
            return True
    return False


class MCTSNode:
    """Một nút trong cây. Không giữ bàn cờ riêng: bàn cờ được dựng lại bằng play/undo khi đi xuống."""

    __slots__ = ("parent", "move", "mover", "children", "untried", "visits", "reward")

    def __init__(self, parent, move, mover, untried):
        self.parent = parent
        self.move = move          # nước đi dẫn tới nút này
        self.mover = mover        # người vừa đi nước đó (None ở gốc)
        self.children = []
        self.untried = untried    # các nước chưa mở rộng
        self.visits = 0
        self.reward = 0.0         # tổng điểm, tính theo góc nhìn của `mover`


class MCTSAgent(Agent):
    """Monte Carlo Tree Search với UCT: Selection -> Expansion -> Simulation -> Backpropagation.

    - Một bàn cờ duy nhất, đi xuống bằng play(), quay lên bằng undo() (không copy bàn cho mỗi nút).
    - Simulation là playout ngẫu nhiên thuần: xáo trộn các ô trống rồi đánh luân phiên tới khi có kết quả.
    - Khi tạo một nút (đúng 1 lần, không phải ở mỗi bước playout): nếu có nước thắng ngay thì chỉ xét nước đó,
      nếu không và đối thủ sắp thắng thì chỉ xét các nước chặn. Đây là luật thắng/chặn trong cây, không phải sửa kết quả.
    - Bàn lớn (> 5x5): các nước trong cây chỉ lấy ở ô cách quân đã đánh <= REGION_DIST; playout vẫn ngẫu nhiên trên mọi ô trống.
    - Chọn nước cuối cùng: nút con được thăm nhiều nhất (robust child).
    """

    name = "MCTS"
    SMALL_BOARD = 25
    REGION_DIST = 2

    def __init__(self, iterations=1000, exploration=math.sqrt(2), seed=None):
        super().__init__()
        if iterations < 1:
            raise ValueError("iterations must be at least 1")
        if exploration < 0:
            raise ValueError("exploration must be non-negative")

        self.iterations = iterations
        self.exploration = exploration
        self.random = random.Random(seed)
        self.nodes = 0

    def choose_move(self, board, time_limit=None):
        if board.is_terminal():
            return None

        work = board.copy()          # không bao giờ làm thay đổi bàn của người gọi
        playable = self.playable_cells(work)
        root = self.new_node(work, None, None, None, playable)
        self.nodes = 1

        if len(root.untried) == 1:   # chỉ còn một lựa chọn (thắng ngay / buộc chặn / nước đầu): khỏi tìm kiếm
            self.stats = {"nodes": 1, "iterations": 0}
            return root.untried[0]

        deadline = None if time_limit is None else time.perf_counter() + time_limit
        done = 0
        for i in range(self.iterations):
            if i > 0 and deadline is not None and time.perf_counter() >= deadline:
                break
            self.run_iteration(work, root, playable)
            done += 1

        self.stats = {"nodes": self.nodes, "iterations": done}
        if not root.children:
            return self.random.choice(root.untried)
        return self.best_child(root).move

    def run_iteration(self, work, root, playable):
        node = root
        depth = 0

        # 1. Selection: đi xuống theo UCT tới nút còn nước chưa mở rộng (hoặc nút lá/kết thúc)
        while not node.untried and node.children:
            node = self.select_child(node)
            work.play(node.move)
            depth += 1

        # 2. Expansion: mở rộng một nước chưa thử
        if node.untried:
            move = node.untried.pop()
            mover = work.player
            work.play(move)
            depth += 1
            child = self.new_node(work, node, move, mover, playable)
            node.children.append(child)
            self.nodes += 1
            node = child

        # 3. Simulation: nếu chưa kết thúc thì đánh ngẫu nhiên tới cuối
        winner = work.winner_ if work.is_terminal() else self.rollout(work)

        # 4. Backpropagation: cộng điểm theo góc nhìn của người đã đi vào từng nút
        leaf = node
        while node is not None:
            node.visits += 1
            if node.mover is not None:
                if winner is None:
                    node.reward += 0.5
                elif winner == node.mover:
                    node.reward += 1.0
            node = node.parent

        for _ in range(depth):
            work.undo()
        return leaf

    def playable_cells(self, board):
        n = board.n
        if n * n <= self.SMALL_BOARD:
            return board.legal_moves()
        if not board.history:
            return [(n // 2, n // 2)]
        return board.candidate_moves(dist=self.REGION_DIST)

    def new_node(self, board, parent, move, mover, playable):
        untried = []
        if not board.is_terminal():
            grid = board.grid
            moves = [m for m in playable if grid[m[0]][m[1]] == 0]
            untried = self.forced_or_all(board, moves)
            self.random.shuffle(untried)
        return MCTSNode(parent, move, mover, untried)

    def forced_or_all(self, board, moves):
        grid, n, k = board.grid, board.n, board.k
        me, opponent = board.player, 3 - board.player

        wins = [m for m in moves if completes_line(grid, n, k, m[0], m[1], me)]
        if wins:
            return wins
        blocks = [m for m in moves if completes_line(grid, n, k, m[0], m[1], opponent)]
        if blocks:
            return blocks
        return moves

    def select_child(self, parent):
        log_parent = math.log(parent.visits)
        best_score = -math.inf
        best_children = []
        for child in parent.children:
            score = child.reward / child.visits + self.exploration * math.sqrt(log_parent / child.visits)
            if score > best_score:
                best_score = score
                best_children = [child]
            elif score == best_score:
                best_children.append(child)
        return self.random.choice(best_children)

    def rollout(self, board):
        empties = board.legal_moves()
        self.random.shuffle(empties)

        played = 0
        for move in empties:
            board.play(move)
            played += 1
            if board.winner_ is not None:
                break
        winner = board.winner_

        for _ in range(played):
            board.undo()
        return winner

    def best_child(self, root):
        best = root.children[0]
        for child in root.children[1:]:
            if child.visits > best.visits or (
                child.visits == best.visits
                and child.reward / child.visits > best.reward / best.visits
            ):
                best = child
        return best
