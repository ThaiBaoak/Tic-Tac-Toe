import random
from .base import Agent


class RandomAgent(Agent):
    name = "Random"

    def choose_move(self, board, time_limit=None):
        self.stats = {"nodes": 0}
        return random.choice(board.legal_moves())