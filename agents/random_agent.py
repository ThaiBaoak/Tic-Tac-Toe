import random

from .base import Agent


class RandomAgent(Agent):
    name = "Random"

    def __init__(self, seed=None):
        super().__init__()
        self.random = random.Random(seed)

    def choose_move(self, board, time_limit=None):
        moves = board.legal_moves()
        self.stats = {"nodes": 0}
        if board.is_terminal() or not moves:
            return None
        return self.random.choice(moves)
