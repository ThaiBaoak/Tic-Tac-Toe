from .random_agent import RandomAgent
from .alphabeta import AlphaBetaAgent

AGENTS = {
    "Random": RandomAgent,
    "Alpha-beta d=2": lambda: AlphaBetaAgent(depth=2),
    "Alpha-beta d=4": lambda: AlphaBetaAgent(depth=4),
}