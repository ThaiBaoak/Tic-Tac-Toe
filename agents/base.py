class Agent:
    name = "Agent"

    def __init__(self):
        self.stats = {}

    def choose_move(self, board, time_limit=None):
        raise NotImplementedError
