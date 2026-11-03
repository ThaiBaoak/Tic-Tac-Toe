from game.board import Board
class Agent:
    def choose_move(self, board):
        raise NotImplementedError
    def alpha_beta_prunning(self, depth, alpha, beta, player):
        r = -1
        c = -1
        if (depth == 0):
            return [r,c,Board.get_score(self,player)]
        else:
            for cell in Board.candidate_moves():
                Board.play(cell[0],cell[1])
                score = self.alpha_beta_prunning(depth-1, alpha, beta, 3-player)

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

                Board.play(cell[0],cell[1])

                if(alpha >= beta):
                    break
        if(player==1):
            return [r,c,alpha]
        else:
            return [r,c,beta]