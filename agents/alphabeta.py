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
        if (depth == 0):
            return [r,c,self.get_score(player)]
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

    