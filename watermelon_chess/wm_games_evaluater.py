import copy

import Arena
from MCTS import MCTS

import numpy as np
from utils import *
from watermelon_chess.alpha_zero_game import WMGame
from watermelon_chess.common import DISTANCE, MODEL_PATH, MOVE_TO_INDEX_DICT
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
        point_status_copy = copy.deepcopy(point_status)
        a, _ = computerMove(point_status_copy, DISTANCE, level)
        if a is None:
            game = WMGame()
            a = RandomPlayer(game).play(point_status)
            return a

        a = MOVE_TO_INDEX_DICT[a]
        return a


class GamesEvaluate:

    @staticmethod
    def execute_game_test(game, neural_net, name_1=None, name_2=None):
        rp = RandomPlayer(game).play
        greedy_player = GreedyPlayer.greedy_action

        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})

        net_player_1 = neural_net(game)
        # None: n1p won 23, rp Won 13, peace 4
        if name_1 is not None:
            net_player_1.load_checkpoint(MODEL_PATH, name_1)

        net_player_2 = neural_net(game)
        if name_2 is not None:
            net_player_2.load_checkpoint(MODEL_PATH, name_2)

        mcts_1 = MCTS(game, net_player_1, args)
        n1p = lambda x: np.argmax(mcts_1.getActionProb(x, temp=0))

        mcts_2 = MCTS(game, net_player_2, args)
        n2p = lambda x: np.argmax(mcts_2.getActionProb(x, temp=0))

        arena = Arena.Arena(n1p, n2p, game)
        one_won, two_won, draws = arena.playGames(100, verbose=False)
        win_rate = round(one_won / (one_won + two_won), 2)
        print(f"n1p won {one_won}, n2p Won {two_won}, peace {draws}, win_rate {win_rate}")

    def wm_pytorch(self):
        self.execute_game_test(WMGame(), WMNNetWrapper, name_1="best.pth.tar")


if __name__ == '__main__':
    GamesEvaluate().wm_pytorch()
