"""
Test bộ đánh giá, Backtracking, MCTS, Random. Chạy từ thư mục gốc repo:
    python -m tests.test_agents
"""
import random
import time

from game.board import Board
from agents.evaluation import LineEvaluator
from agents.backtracking import BacktrackingAgent
from agents.mcts_agent import MCTSAgent
from agents.random_agent import RandomAgent


def make_board(n, k, moves):
    b = Board(n, k)
    for m in moves:
        b.play(m)
    return b


def play_game(agent_x, agent_o, n, k):
    b = Board(n, k)
    agents = {1: agent_x, 2: agent_o}
    while not b.is_terminal():
        b.play(agents[b.player].choose_move(b.copy()))
    return b.winner_


# ---------- bộ đánh giá gia tăng ----------
def test_evaluator_incremental_matches_recompute():
    rng = random.Random(0)
    for _ in range(200):
        n, k = rng.choice([(3, 3), (5, 4), (7, 5), (9, 5)])
        b, ev, stack = Board(n, k), LineEvaluator(n, k), []
        for _ in range(rng.randint(1, n * n // 2)):
            m, p = rng.choice(b.legal_moves()), b.player
            b.play(m)
            ev.place(m[0], m[1], p)
            stack.append((m, p))
            if rng.random() < 0.3:
                m, p = stack.pop()
                b.undo()
                ev.remove(m[0], m[1], p)
        ref = LineEvaluator(n, k)
        ref.reset(b.grid)
        assert (ev.score, ev.threats, ev.count) == (ref.score, ref.threats, ref.count)


# ---------- Backtracking ----------
def test_backtracking_win_and_block():
    win = make_board(5, 3, [(0, 0), (4, 4), (0, 1), (4, 3)])
    assert BacktrackingAgent(2).choose_move(win.copy()) == (0, 2)
    block = make_board(5, 3, [(0, 0), (4, 4), (0, 1)])
    assert BacktrackingAgent(2).choose_move(block.copy()) == (0, 2)


def test_backtracking_3x3_perfect_play_is_draw():
    assert play_game(BacktrackingAgent(9), BacktrackingAgent(9), 3, 3) is None


def test_backtracking_board_restored():
    b = make_board(6, 4, [(2, 2), (3, 3), (2, 3)])
    before = ([r[:] for r in b.grid], b.player, b.history[:])
    BacktrackingAgent(2).choose_move(b)
    assert (b.grid, b.player, b.history) == before


# ---------- MCTS ----------
def test_mcts_win_in_one():
    b = make_board(5, 3, [(0, 0), (4, 4), (0, 1), (4, 3)])
    assert MCTSAgent(200, seed=0).choose_move(b.copy()) == (0, 2)


def test_mcts_block():
    b = make_board(5, 3, [(0, 0), (4, 4), (0, 1)])
    assert MCTSAgent(200, seed=0).choose_move(b.copy()) == (0, 2)


def test_mcts_takes_win_over_block():
    # X sắp thắng ở (0,2) nhưng O thắng ngay ở (4,2), O phải thắng chứ không chặn
    b = make_board(5, 3, [(0, 0), (4, 4), (0, 1), (4, 3)])
    b.play((2, 2))
    assert b.player == 2
    assert MCTSAgent(200, seed=0).choose_move(b.copy()) == (4, 2)


def test_mcts_legal_and_board_restored():
    rng = random.Random(1)
    for _ in range(5):
        b = Board(8, 5)
        for _ in range(rng.randint(1, 10)):
            b.play(rng.choice(b.legal_moves()))
            if b.is_terminal():
                break
        if b.is_terminal():
            continue
        before = ([r[:] for r in b.grid], b.player, b.history[:], b.winner_)
        move = MCTSAgent(100, seed=0).choose_move(b)
        assert b.grid[move[0]][move[1]] == 0
        assert (b.grid, b.player, b.history, b.winner_) == before


def test_mcts_terminal_returns_none():
    b = make_board(3, 3, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    assert MCTSAgent(10).choose_move(b) is None


def test_mcts_time_limit():
    b = make_board(10, 5, [(5, 5), (5, 6)])
    t0 = time.perf_counter()
    MCTSAgent(10 ** 6, seed=0).choose_move(b, time_limit=0.3)
    assert time.perf_counter() - t0 < 1.0


def test_mcts_never_loses_to_random_3x3():
    for side in (1, 2):
        for seed in range(5):
            mcts, rnd = MCTSAgent(300, seed=seed), RandomAgent(seed)
            w = play_game(mcts, rnd, 3, 3) if side == 1 else play_game(rnd, mcts, 3, 3)
            assert w != 3 - side


# ---------- Random ----------
def test_random_legal_and_seeded():
    b = make_board(4, 3, [(0, 0), (1, 1)])
    m1, m2 = RandomAgent(5).choose_move(b), RandomAgent(5).choose_move(b)
    assert m1 == m2 and b.grid[m1[0]][m1[1]] == 0


def test_random_terminal_returns_none():
    b = make_board(3, 3, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    assert RandomAgent(0).choose_move(b) is None


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t0 = time.perf_counter()
        t()
        print(f"PASS {t.__name__} ({time.perf_counter() - t0:.2f}s)")
    print("TẤT CẢ ĐỀU ĐẠT")
