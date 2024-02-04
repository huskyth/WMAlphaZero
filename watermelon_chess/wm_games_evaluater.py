import Arena
from MCTS import MCTS

import numpy as np
from utils import *
from watermelon_chess.alpha_zero_game import WMGame
from watermelon_chess.common import DISTANCE
from watermelon_chess.control import computerMove
from watermelon_chess.models.nn_net import WMNNetWrapper


class RandomPlayer:
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a] != 1:
            a = np.random.randint(self.game.getActionSize())
        return a


class GreedyPlayer:
    @staticmethod
    def greedy_action(point_status):
        level = 1
        return computerMove(point_status, DISTANCE, level)


class GamesEvaluate:

    @staticmethod
    def execute_game_test(game, neural_net):
        rp = RandomPlayer(game).play

        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
        mcts = MCTS(game, neural_net(game), args)
        n1p = lambda x: np.argmax(mcts.getActionProb(x, temp=0))

        arena = Arena.Arena(n1p, rp, game)
        print(arena.playGames(2, verbose=False))

    def wm_pytorch(self):
        self.execute_game_test(WMGame(), WMNNetWrapper)


if __name__ == '__main__':
    GamesEvaluate().wm_pytorch()
