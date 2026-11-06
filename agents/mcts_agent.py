import math
import random

from .base import Agent


class MCTSNode:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.total_reward = 0.0

        if board.is_terminal():
            self.untried_moves = []
        else:
            self.untried_moves = board.legal_moves()

    def player_just_moved(self):
        return 3 - self.board.player


class MCTSAgent(Agent):
    def __init__(self, iterations=1000, exploration=math.sqrt(2), seed=None):
        if iterations < 1:
            raise ValueError("iterations must be at least 1")
        if exploration < 0:
            raise ValueError("exploration must be non-negative")

        self.iterations = iterations
        self.exploration = exploration
        self.random = random.Random(seed)

    def choose_move(self, board):
        if board.is_terminal():
            return None

        legal_moves = board.legal_moves()
        forced_move = self.find_forced_move(board, legal_moves)
        if forced_move is not None:
            return forced_move

        root_player = board.player
        root = MCTSNode(board.copy())

        for _ in range(self.iterations):
            node = root

            # 1 Selection
            while not node.board.is_terminal() and len(node.untried_moves) == 0:
                node = self.select_child(node)

            # 2 Expansion
            if not node.board.is_terminal() and len(node.untried_moves) > 0:
                node = self.expand(node)

            # 3 Simulation
            winner = self.rollout(node.board)

            # 4 Backpropagation
            self.backpropagate(node, winner, root_player)

        if len(root.children) == 0:
            return None

        best_child = root.children[0]
        for child in root.children[1:]:
            if child.visits > best_child.visits:
                best_child = child
            elif child.visits == best_child.visits:
                child_average = child.total_reward / child.visits
                best_average = best_child.total_reward / best_child.visits
                if child_average > best_average:
                    best_child = child

        return best_child.move

    def select_child(self, parent):
        best_score = -float("inf")
        best_children = []

        for child in parent.children:
            if child.visits == 0:
                score = float("inf")
            else:
                exploitation = child.total_reward / child.visits
                exploration = self.exploration * math.sqrt(
                    math.log(parent.visits) / child.visits
                )
                score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_children = [child]
            elif score == best_score:
                best_children.append(child)

        return self.random.choice(best_children)

    def expand(self, parent):
        move = self.random.choice(parent.untried_moves)
        parent.untried_moves.remove(move)

        next_board = parent.board.copy()
        next_board.play(move)

        child = MCTSNode(next_board, parent, move)
        parent.children.append(child)
        return child

    def rollout(self, board):
        simulated_board = board.copy()

        while not simulated_board.is_terminal():
            moves = simulated_board.legal_moves()
            forced_move = self.find_forced_move(simulated_board, moves)

            if forced_move is not None:
                move = forced_move
            else:
                move = self.random.choice(moves)

            simulated_board.play(move)

        return simulated_board.winner_

    def find_forced_move(self, board, moves):
        # Ưu tiên thắng ngay, sau đó mới chặn nước thắng của đối thủ.
        for move in moves:
            if self.is_winning_move(board, move, board.player):
                return move

        opponent = 3 - board.player
        for move in moves:
            if self.is_winning_move(board, move, opponent):
                return move

        return None

    def is_winning_move(self, board, move, player):
        row, column = move
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            count = 1

            for sign in [1, -1]:
                r = row + sign * dr
                c = column + sign * dc

                while 0 <= r < board.n and 0 <= c < board.n:
                    if board.grid[r][c] != player:
                        break

                    count += 1
                    r += sign * dr
                    c += sign * dc

            if count >= board.k:
                return True

        return False

    def backpropagate(self, node, winner, root_player):
        while node is not None:
            node.visits += 1

            # mỗi nút lưu điểm theo người vừa tạo ra nút đó
            if node.parent is None:
                player = root_player
            else:
                player = node.player_just_moved()

            if winner is None:
                node.total_reward += 0.5
            elif winner == player:
                node.total_reward += 1.0

            node = node.parent
