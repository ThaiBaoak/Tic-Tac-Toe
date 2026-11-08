"""
Kiểm tra AlphaBetaAgent. Chạy từ thư mục gốc repo:
    python -m tests.test_alphabeta        (chạy hết, in kết quả)
    python -m pytest tests -q             (nếu đã cài pytest)
"""
import random
import time

from game.board import Board
from agents.alphabeta import AlphaBetaAgent, INF


# ---------- công cụ dùng chung ----------
def make_board(n, k, moves):
    b = Board(n, k)
    for m in moves:
        b.play(m)
    return b


def random_position(n, k, plies, rng):
    """Tạo thế cờ ngẫu nhiên chưa kết thúc bằng cách đi ngẫu nhiên."""
    while True:
        b = Board(n, k)
        for _ in range(plies):
            if b.is_terminal():
                break
            b.play(rng.choice(b.candidate_moves()))
        if not b.is_terminal():
            return b


def minimax(agent, depth, player, counter):
    """Minimax THUẦN (không cắt tỉa), cùng hàm đánh giá với alpha-beta.
    Dùng làm đáp án chuẩn để đối chiếu."""
    counter[0] += 1
    b = agent.board
    if depth == 0 or b.is_terminal():
        return agent.get_score(player)
    vals = []
    for cell in b.candidate_moves():
        b.play(cell)
        vals.append(minimax(agent, depth - 1, 3 - player, counter))
        b.undo()
    return max(vals) if player == 1 else min(vals)


# ---------- 1. Thế cờ có đáp án rõ ràng ----------
def test_win_in_one():
    # X có (0,0),(0,1), đến lượt X -> phải đi (0,2)
    b = make_board(5, 3, [(0, 0), (4, 4), (0, 1), (4, 3)])
    assert AlphaBetaAgent(2).choose_move(b.copy()) == (0, 2)


def test_block_opponent():
    # O phải chặn (0,2), nếu không X thắng
    b = make_board(5, 3, [(0, 0), (4, 4), (0, 1)])
    assert AlphaBetaAgent(2).choose_move(b.copy()) == (0, 2)


def test_win_as_O():
    # O có (4,3),(4,4)... đến lượt O thắng ở (4,2)
    b = make_board(5, 3, [(0, 0), (4, 4), (2, 0), (4, 3), (0, 4)])
    assert b.player == 2
    assert AlphaBetaAgent(2).choose_move(b.copy()) == (4, 2)


# ---------- 2. Tính hợp lệ và không làm hỏng bàn ----------
def test_move_legal_and_board_restored():
    rng = random.Random(0)
    for _ in range(10):
        b = random_position(7, 5, rng.randint(2, 12), rng)
        before = ([r[:] for r in b.grid], b.player, b.history[:])
        agent = AlphaBetaAgent(2)
        move = agent.choose_move(b)             # truyền thẳng bàn, không copy
        assert move in [(r, c) for r in range(7) for c in range(7)
                        if before[0][r][c] == 0], "nước đi không hợp lệ"
        after = (b.grid, b.player, b.history)
        assert after == before, "play/undo không cân bằng, bàn bị thay đổi"


# ---------- 3. Đối chiếu với minimax thuần (kiểm tra quan trọng nhất) ----------
def test_same_value_as_minimax_and_fewer_nodes():
    rng = random.Random(1)
    total_ab = total_mm = 0
    for _ in range(25):
        n, k = rng.choice([(4, 3), (5, 4)])
        b = random_position(n, k, rng.randint(1, 6), rng)
        for depth in (2, 3):
            agent = AlphaBetaAgent(depth)
            agent.board = b.copy()
            agent.nodes = 0
            ab_value = agent.alpha_beta_prunning(depth, -INF, INF, agent.board.player)[2]
            total_ab += agent.nodes

            cnt = [0]
            agent.board = b.copy()
            mm_value = minimax(agent, depth, agent.board.player, cnt)
            total_mm += cnt[0]
            assert ab_value == mm_value, (n, k, depth, ab_value, mm_value)
    assert total_ab < total_mm, "cắt tỉa không giảm được số node"
    print(f"  số node alpha-beta {total_ab} < minimax {total_mm}")


# ---------- 4. Chơi cả ván ----------
def play_game(agent_x, agent_o, n, k):
    b = Board(n, k)
    agents = {1: agent_x, 2: agent_o}
    while not b.is_terminal():
        b.play(agents[b.player].choose_move(b.copy()))
    return b.winner_


class RandomPlayer:
    def __init__(self, rng):
        self.rng = rng

    def choose_move(self, board):
        return self.rng.choice(board.legal_moves())


def test_never_loses_to_random():
    rng = random.Random(2)
    for n, k in [(3, 3), (5, 4), (7, 5)]:
        for side in (1, 2):
            for _ in range(5):
                ab, rd = AlphaBetaAgent(2), RandomPlayer(rng)
                w = play_game(ab, rd, n, k) if side == 1 else play_game(rd, ab, n, k)
                assert w != 3 - side, f"alpha-beta thua random ({n}x{n}, k={k})"


def test_3x3_perfect_play_is_draw():
    # 3x3 duyệt hết cây (độ sâu 9): hai bên chơi tối ưu phải HÒA
    w = play_game(AlphaBetaAgent(9), AlphaBetaAgent(9), 3, 3)
    assert w is None, "3x3 chơi tối ưu phải hòa"


def test_deeper_is_not_worse():
    rng = random.Random(3)
    score = 0
    for first in (1, 2):
        for _ in range(3):
            deep, shallow = AlphaBetaAgent(3), AlphaBetaAgent(1)
            w = (play_game(deep, shallow, 5, 4) if first == 1
                 else play_game(shallow, deep, 5, 4))
            if w == first:
                score += 1
            elif w is not None:
                score -= 1
    assert score >= 0, "độ sâu lớn hơn lại yếu hơn độ sâu nhỏ"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t0 = time.perf_counter()
        t()
        print(f"PASS {t.__name__} ({time.perf_counter() - t0:.2f}s)")
    print("TẤT CẢ ĐỀU ĐẠT")